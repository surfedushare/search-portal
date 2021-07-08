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

    def test_synchronous_download_pipeline(self):
        resource = "core.fileresource"
        processor = HttpPipelineProcessor({
            "pipeline_app_label": "core",
            "batch_size": 5,
            "asynchronous": False,
            "resource_process": {
                "resource": resource,
                "method": "get",
                "args": ["$.url"],
                "kwargs": {},
                "result_key": "download"
            }
        })
        processor(self.collection.documents)
        self.assertEqual(Batch.objects.count(), 3)
        self.assertEqual(ProcessResult.objects.count(), 0)
        self.assertEqual(self.collection.documents.count(), 11)
        for document in self.collection.documents.all():
            if document.id != 222473:
                self.assertIn("download", document.pipeline)
                download_pipeline = document.pipeline["download"]
                self.assertEqual(download_pipeline["resource"], "core.fileresource")
                self.assertIsInstance(download_pipeline["id"], int)
                self.assertTrue(download_pipeline["success"])
            else:
                self.assertIsInstance(document.pipeline, dict)
                self.assertNotIn("download", document.pipeline)

    @patch("core.processors.pipeline.base.chord", return_value=chord_mock_result)
    def test_asynchronous_pipeline(self, chord_mock):
        """
        This test only asserts if Celery is used as expected.
        See synchronous test for actual result testing.
        """
        resource = "core.fileresource"
        processor = HttpPipelineProcessor({
            "pipeline_app_label": "core",
            "batch_size": 5,
            "resource_process": {
                "resource": resource,
                "method": "get",
                "args": ["$.url"],
                "kwargs": {},
                "result": "download"
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
