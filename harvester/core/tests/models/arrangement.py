from django.test import TestCase

from core.models import Arrangement


class TestArrangement(TestCase):

    fixtures = ["datasets-history", "surf-oaipmh-2020-01-01", "resources"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package = Arrangement.objects.get(id=92378)

    def test_unpack_package_documents(self):
        reference_id = "aaaaaaaa-aaaa-aaaa-aaaaaaaa-aaaaaaaa"
        base_url = "http://localhost/test"
        documents = self.package.unpack_package_documents(reference_id, base_url)
        self.assertEqual(len(documents), 6)
        expected_titles = {
            "Inleiding",
            "Leerdoelen",
            "Opdrachten",
            "Bronnen",
            "Handleiding voor de opleider",
            "Colofon",
        }
        expected_links = {
            "#!page-2935729",
            "#!page-2935768",
            "#!page-2935734",
            "#!page-3703806",
            "#!page-2935733",
            "#!page-colofon",
        }
        for document in documents:
            self.assertEqual(document["is_part_of"], reference_id)
            self.assertIn(document["title"], expected_titles)
            self.assertIn(document["_id"].replace(reference_id, ""), expected_links)
            self.assertIn(document["url"].replace(base_url, ""), expected_links)
            if document["title"] == "Colofon":
                self.assertFalse(document["text"])
            else:
                self.assertTrue(document["text"])
