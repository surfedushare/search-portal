from unittest.mock import patch
from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from core.constants import HarvestStages
from core.models import Dataset, FileResource, TikaResource


class TestResetDataset(TestCase):
    """
    Testing that almost all data disappears, but cache remains.
    State should also get reset.
    """

    fixtures = ["datasets-history", "resources"]

    @patch("core.utils.previews.default_storage")
    @patch("datagrowth.resources.http.files.default_storage")
    def test_reset(self, resource_storage_mock, preview_storage_mock):
        file_id = 12033
        tika_id = 75
        try:
            FileResource.objects.get(id=file_id)
            TikaResource.objects.get(id=tika_id)
        except (FileResource.DoesNotExist, TikaResource.DoesNotExist):
            self.fail("Resources are missing before start of reset test")

        dataset = Dataset.objects.get(id=19)
        dataset.reset()
        try:
            FileResource.objects.get(id=file_id)
            TikaResource.objects.get(id=tika_id)
        except (FileResource.DoesNotExist, TikaResource.DoesNotExist):
            self.fail("Resources are missing after reset")
        self.assertEqual(resource_storage_mock.delete.call_count, 0, "Expected Document files to remain after a reset")
        self.assertEqual(preview_storage_mock.delete.call_count, 0, "Expected preview files to remain after a reset")
        self.assertEqual(dataset.collection_set.count(), 0)
        self.assertEqual(dataset.document_set.count(), 0)
        self.assertEqual(dataset.harvest_set.count(), 2)
        for harvest in dataset.harvest_set.all():
            self.assertEqual(harvest.latest_update_at, make_aware(datetime(day=1, month=1, year=1970)))
            self.assertIsNone(harvest.harvested_at)
            self.assertEqual(harvest.stage, HarvestStages.NEW)
