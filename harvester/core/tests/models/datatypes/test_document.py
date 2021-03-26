from unittest.mock import patch

from django.test import TestCase

from core.models import Document, FileResource, TikaResource


class TestDocument(TestCase):

    fixtures = ["datasets-history", "resources"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.instance = Document.objects.get(id=222318)

    @patch("core.utils.previews.default_storage")
    @patch("datagrowth.resources.http.files.default_storage")
    def test_delete(self, resource_storage_mock, preview_storage_mock):
        file_id = 12033
        tika_id = 75
        try:
            FileResource.objects.get(id=file_id)
            TikaResource.objects.get(id=tika_id)
        except (FileResource.DoesNotExist, TikaResource.DoesNotExist):
            self.fail("Resources are missing before start of deletion test")
        self.instance.id = 666
        self.instance.save()
        self.instance.delete()
        self.assertIsNotNone(self.instance.deleted_at)
        self.instance.delete()
        try:
            FileResource.objects.get(id=file_id)
            self.fail("Expected file resource to be deleted after Document deletion")
        except FileResource.DoesNotExist:
            pass
        try:
            TikaResource.objects.get(id=tika_id)
            self.fail("Expected Tika resource to be deleted after Document deletion")
        except TikaResource.DoesNotExist:
            pass
        self.assertEqual(resource_storage_mock.delete.call_count, 1)
        self.assertEqual(preview_storage_mock.delete.call_count, 4)

    @patch("core.utils.previews.default_storage")
    @patch("datagrowth.resources.http.files.default_storage")
    def test_delete_missing_resources(self, resource_storage_mock, preview_storage_mock):
        file_id = 12033
        tika_id = 75
        try:
            FileResource.objects.get(id=file_id).delete()
            TikaResource.objects.get(id=tika_id).delete()
        except (FileResource.DoesNotExist, TikaResource.DoesNotExist):
            self.fail("Resources are missing before start of deletion test")
        self.instance.id = 666
        self.instance.properties["preview_path"] = None
        self.instance.save()
        self.instance.delete()
        self.assertEqual(resource_storage_mock.delete.call_count, 1)
        self.assertEqual(preview_storage_mock.delete.call_count, 0)
