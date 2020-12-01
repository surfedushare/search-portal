from django.test import TestCase

from core.tests.factories import DocumentFactory, DatasetFactory
from core.models import Document


class TestDocument(TestCase):

    def test_find_by_mimetype(self):
        dataset = DatasetFactory.create()
        document_with_website = DocumentFactory.create(dataset=dataset, properties={"mime_type": "text/html"})
        DocumentFactory.create(dataset=dataset, properties={"mime_type": "foo/bar"})
        documents = Document.get_by_mime_type("text/html").filter(dataset=dataset)
        self.assertEqual(list(documents), list([document_with_website]))
