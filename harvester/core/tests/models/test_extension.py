from collections import Generator

from django.test import TestCase

from core.models import Extension


class TestExtension(TestCase):

    fixtures = ["datasets-history"]

    def setUp(self):
        super().setUp()
        self.extension = Extension.objects.get(id="custom-extension")

    def test_to_search(self):
        extension_generator = self.extension.to_search()
        self.assertIsInstance(extension_generator, Generator)
        extension_search = list(extension_generator)[0]
        self.assertEqual(extension_search["title"], "New! New! New! Extended titles!")
        self.assertEqual(extension_search["authors"], [{"name": "The Extension Man"}])
        self.assertEqual(extension_search["keywords"], ["exercise", "extended"])
        self.assertEqual(sorted(extension_search["is_part_of"]), ["parent"])
        self.assertEqual(sorted(extension_search["has_parts"]), ["child", "part"])
        self.assertEqual(extension_search["parties"], [{"name": "The Extension Party"}])
        self.assertEqual(extension_search["research_themes"], ["theme", "extended"])
