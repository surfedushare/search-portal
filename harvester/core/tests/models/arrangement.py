from django.test import TestCase

from core.models import Arrangement


class TestArrangement(TestCase):

    fixtures = ["datasets-history", "surf-oaipmh-2020-01-01", "resources"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package = Arrangement.objects.get(id=92378)

    def test_unpack_package_documents(self):
        documents = self.package.unpack_package_documents("http://localhost/test")
        self.assertEqual(len(documents), 6)
        expected_titles = {
            "Inleiding",
            "Leerdoelen",
            "Opdrachten",
            "Bronnen",
            "Handleiding voor de opleider",
            "Colofon",
        }
        expected_urls = {
            "http://localhost/test#!page-2935729",
            "http://localhost/test#!page-2935768",
            "http://localhost/test#!page-2935734",
            "http://localhost/test#!page-3703806",
            "http://localhost/test#!page-2935733",
            "http://localhost/test#!page-colofon",
        }
        for document in documents:
            self.assertIn(document["title"], expected_titles)
            self.assertIn(document["url"], expected_urls)
            if document["title"] == "Colofon":
                self.assertFalse(document["text"])
            else:
                self.assertTrue(document["text"])
