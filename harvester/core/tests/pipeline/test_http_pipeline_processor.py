from unittest.mock import patch, MagicMock

from django.test import TestCase
from celery.canvas import Signature

from core.models import Collection, Batch, ProcessResult
from core.processors import HttpPipelineProcessor


chord_mock_result = MagicMock()


class TestHttpPipelineProcessor(TestCase):

    fixtures = ["datasets-history", "resources-basic-initial", "resources-basic-delta"]

    def setUp(self):
        super().setUp()
        self.collection = Collection.objects.get(id=171)

    @patch("core.models.resources.basic.HttpTikaResource._send")
    def test_synchronous_tika_pipeline(self, send_mock):
        resource = "core.httptikaresource"
        processor = HttpPipelineProcessor({
            "pipeline_app_label": "core",
            "pipeline_phase": "tika",
            "batch_size": 5,
            "asynchronous": False,
            "retrieve_data": {
                "resource": resource,
                "method": "post",
                "args": [],
                "kwargs": {"url": "$.url"},
            },
            "contribute_data": {
                "extractor": "ExtractProcessor.extract_from_resource",
                "to_property": "text",
                "objective": {
                    "@": "$",
                    "text": "$.text"
                }
            }
        })
        processor(self.collection.documents)
        self.assertEqual(Batch.objects.count(), 3)
        self.assertEqual(ProcessResult.objects.count(), 0)
        self.assertEqual(self.collection.documents.count(), 11)
        for document in self.collection.documents.all():
            self.assertIn("tika", document.pipeline)
            tika_pipeline = document.pipeline["tika"]
            self.assertEqual(tika_pipeline["resource"], "core.httptikaresource")
            self.assertIsInstance(tika_pipeline["id"], int)
            self.assertIsInstance(tika_pipeline["success"], bool)
        self.assertEqual(send_mock.call_count, 2, "Expected two erroneous resources to retry")

    @patch("core.processors.pipeline.base.chord", return_value=chord_mock_result)
    def test_asynchronous_pipeline(self, chord_mock):
        """
        This test only asserts if Celery is used as expected.
        See synchronous test for actual result testing.
        """
        resource = "core.httptikaresource"
        processor = HttpPipelineProcessor({
            "pipeline_app_label": "core",
            "pipeline_phase": "tika",
            "batch_size": 5,
            "asynchronous": True,
            "retrieve_data": {
                "resource": resource,
                "method": "post",  # TODO: default?
                "args": [],
                "kwargs": {"url": "$.url"},
            },
            "contribute_data": {
                "extractor": "ExtractProcessor.extract_from_resource",  # TODO: default?
                "to_property": None,  # TODO: default
                "objective": {
                    "@": "$",
                    "text": "$.text"
                }
            }
        })
        task = processor(self.collection.documents)
        task.get()
        self.assertEqual(chord_mock.call_count, 1)
        chord_call = chord_mock.call_args_list[0]
        chord_call_args = chord_call.args
        self.assertEqual(len(chord_call_args), 1)
        for ix, signature in enumerate(chord_call_args[0]):
            self.assertIsInstance(signature, Signature)
            self.assertEqual(signature.name, "pipeline_process_and_merge")
            self.assertEqual(signature.args, (ix+1,))
            self.assertIn("config", signature.kwargs)
        self.assertEqual(chord_mock_result.call_count, 1)
        chord_result_call = chord_mock_result.call_args_list[0]
        chord_result_call_args = chord_result_call.args
        self.assertEqual(len(chord_result_call_args), 1)
        finish_signature = chord_result_call_args[0]
        self.assertIsInstance(finish_signature, Signature)
        self.assertEqual(finish_signature.name, "pipeline_full_merge")
        self.assertEqual(finish_signature.args, ("HttpPipelineProcessor",))
        self.assertIn("config", finish_signature.kwargs)
