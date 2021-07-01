from django.test import TestCase

from core.models import Collection, Batch, ProcessResult
from core.processors import HttpPipelineProcessor


class TestHttpPipelineProcessor(TestCase):

    fixtures = ["datasets-history"]

    def setUp(self):
        super().setUp()
        self.collection = Collection.objects.get(id=171)

    def test_synchronous_update_pipeline(self):
        processor = HttpPipelineProcessor({
            "pipeline_app_label": "core",
            "batch_size": 2,
            "asynchronous": False
        })
        processor(self.collection.documents)
        self.assertEqual(self.collection.documents.count(), 3)
        self.assertEqual(Batch.objects.count(), 2)
        self.assertEqual(ProcessResult.objects.count(), 3)

    def test_asynchronous_update_pipeline(self):
        self.fail("here we are")
        processor = HttpPipelineProcessor({
            "pipeline_app_label": "core",
            "batch_size": 2
        })
        task = processor(self.collection.documents)
        task()
        self.assertEqual(self.collection.documents.count(), 3)
        self.assertEqual(Batch.objects.count(), 2)
        self.assertEqual(ProcessResult.objects.count(), 3)
