from collections import Generator

from django.test import TestCase

from core.models import Collection, Document, Extension


class TestDocument(TestCase):

    fixtures = ["datasets-history"]

    def setUp(self):
        super().setUp()
        self.document = Document.objects.get(id=222318)
        self.extended_document = Document.objects.get(id=222317)

    def test_to_search(self):
        search_document_generator = self.document.to_search()
        self.assertIsInstance(search_document_generator, Generator)
        search_document = list(search_document_generator)[0]
        self.assertEqual(search_document["state"], "active")
        self.assertEqual(search_document["authors"], [])
        self.assertEqual(search_document["material_types"], ["unknown"])
        self.assertEqual(search_document["keywords"], ["Video", "Practicum clip", "Instructie clip"])
        self.assertEqual(search_document["is_part_of"], ["part"])
        self.assertEqual(search_document["has_parts"], ["part"])
        self.assertEqual(search_document["parties"], [])
        self.assertEqual(search_document["research_themes"], ["research"])
        extended_search_document_generator = self.extended_document.to_search()
        self.assertIsInstance(extended_search_document_generator, Generator)
        extended_search_document = list(extended_search_document_generator)[0]
        self.assertEqual(extended_search_document["state"], "active")
        self.assertEqual(extended_search_document["authors"], [{"name": "The Extension Man"}])
        self.assertEqual(extended_search_document["material_types"], ["kennisoverdracht"])
        self.assertEqual(extended_search_document["keywords"], ["exercise", "extended"])
        self.assertEqual(sorted(extended_search_document["is_part_of"]), ["parent", "part"])
        self.assertEqual(sorted(extended_search_document["has_parts"]), ["child", "part"])
        self.assertEqual(extended_search_document["parties"], [{"name": "The Extension Party"}])
        self.assertEqual(extended_search_document["research_themes"], ["theme", "extended"])

    def test_to_search_delete(self):
        self.document.properties["state"] = "deleted"
        search_document_generator = self.document.to_search()
        search_document = list(search_document_generator)[0]
        self.assertEqual(search_document["_id"], "5be6dfeb-b9ad-41a8-b4f5-94b9438e4257")
        self.assertEqual(search_document["_op_type"], "delete")

    def test_to_search_preexisting_extension(self):
        extension_id = "custom-extension"
        document = Document.objects.create(
            collection=Collection.objects.last(),
            extension=Extension.objects.get(id=extension_id),
            reference=extension_id,
            properties={
                "state": "active",
                "external_id": extension_id,
                "language": {"metadata": "en"},
                "title": "will get overridden",
                "description": "test description"
            }
        )
        search_document_generator = document.to_search()
        self.assertIsInstance(search_document_generator, Generator)
        search_document = list(search_document_generator)[0]
        self.assertEqual(search_document["title"], "New! New! New! Extended titles!",
                         "Expected title to be taken from Extension")
        self.assertEqual(search_document["description"], "test description",
                         "Expected description to be taken from Document")
