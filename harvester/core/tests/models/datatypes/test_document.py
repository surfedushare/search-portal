from unittest.mock import patch

from django.test import TestCase

from core.models import Document


class TestDocument(TestCase):

    fixtures = ["datasets-history", "resources"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.instance = Document.objects.get(id=222318)

    @patch("core.utils.previews.default_storage")
    def test_delete(self, preview_storage_mock):
        self.instance.delete()
        self.assertEqual(preview_storage_mock.delete.call_count, 4)
