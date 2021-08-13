from collections import Generator

from django.test import TestCase

from core.models import Document


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
        self.assertEqual(search_document["authors"], [])
        self.assertEqual(search_document["material_types"], ["unknown"])
        extended_search_document_generator = self.extended_document.to_search()
        self.assertIsInstance(extended_search_document_generator, Generator)
        extended_search_document = list(extended_search_document_generator)[0]
        self.assertEqual(extended_search_document["authors"], [{"name": "The Extension Man"}])
        self.assertEqual(extended_search_document["material_types"], ["kennisoverdracht"])
