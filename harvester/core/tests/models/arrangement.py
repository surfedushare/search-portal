from django.test import TestCase

from core.models import Arrangement, FileResource


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
        expected_ids = {
            "aaaaaaaa-aaaa-aaaa-aaaaaaaa-aaaaaaaa-page-2935729",
            "aaaaaaaa-aaaa-aaaa-aaaaaaaa-aaaaaaaa-page-2935768",
            "aaaaaaaa-aaaa-aaaa-aaaaaaaa-aaaaaaaa-page-2935734",
            "aaaaaaaa-aaaa-aaaa-aaaaaaaa-aaaaaaaa-page-3703806",
            "aaaaaaaa-aaaa-aaaa-aaaaaaaa-aaaaaaaa-page-2935733",
            "aaaaaaaa-aaaa-aaaa-aaaaaaaa-aaaaaaaa-page-colofon",
        }
        for document in documents:
            self.assertEqual(document["is_part_of"], reference_id)
            self.assertIn(document["title"], expected_titles)
            self.assertIn(document["_id"], expected_ids)
            self.assertIn(document["url"].replace(base_url, ""), expected_links)
            if document["title"] == "Colofon":
                self.assertFalse(document["text"])
            else:
                self.assertTrue(document["text"])

    def test_unpack_package_documents_file_download_error(self):
        # Setting the package file download resource to failed state
        _, file_resource_id = self.package.base_document.properties["pipeline"]["file"]["resource"]
        file_resource = FileResource.objects.get(id=file_resource_id)
        file_resource.status = 404
        file_resource.save()
        # And executing tests with that
        reference_id = "aaaaaaaa-aaaa-aaaa-aaaaaaaa-aaaaaaaa"
        base_url = "http://localhost/test"
        documents = self.package.unpack_package_documents(reference_id, base_url)
        self.assertEqual(len(documents), 0)

    def test_unpack_package_documents_package_download_error(self):
        # Setting the package file download resource to failed state
        _, file_resource_id = self.package.base_document.properties["pipeline"]["package_file"]["resource"]
        file_resource = FileResource.objects.get(id=file_resource_id)
        file_resource.status = 404
        file_resource.save()
        # And executing tests with that
        reference_id = "aaaaaaaa-aaaa-aaaa-aaaaaaaa-aaaaaaaa"
        base_url = "http://localhost/test"
        documents = self.package.unpack_package_documents(reference_id, base_url)
        self.assertEqual(len(documents), 0)
