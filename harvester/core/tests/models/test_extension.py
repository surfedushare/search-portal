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

    def test_delete_addition(self):
        self.extension.delete()
        self.assertIsNotNone(self.extension.deleted_at)
        to_search_list = list(self.extension.to_search())
        self.assertEqual(len(to_search_list), 1)
        self.assertEqual(to_search_list[0], {"_op_type": "delete", "_id": self.extension.id})
        self.extension.restore()
        self.assertIsNone(self.extension.deleted_at)
        to_search_list = list(self.extension.to_search())
        self.assertEqual(len(to_search_list), 1)
        self.assertNotEqual(to_search_list[0], {"_op_type": "delete", "_id": self.extension.id})
        self.extension.delete()
        self.extension.delete()
        self.assertEqual(Extension.objects.filter(id="custom-extension").count(), 0)

    def test_delete(self):
        extension = Extension.objects.get(id="5af0e26f-c4d2-4ddd-94ab-7dd0bd531751")
        extension.delete()
        self.assertEqual(Extension.objects.filter(id="5af0e26f-c4d2-4ddd-94ab-7dd0bd531751").count(), 0)
