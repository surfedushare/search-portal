from unittest import skipIf
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

from django.conf import settings
from django.test import TestCase


def json_data():
    return {
        "count": 501,  # a fake count to trigger pagination
        "results": [
            {
                "id": 1,
                "reference": "external-id:1",
                "language": "nl",
                "created_at": "2021-10-25T14:30:49.565775Z",
                "modified_at": "2021-10-25T14:31:49.565784Z"
            },
            {
                "id": 2,
                "reference": "external-id.2",
                "language": "en",
                "created_at": "2021-10-25T14:30:49.565775Z",
                "modified_at": "2021-10-25T14:31:49.565784Z"
            },
            {
                "id": 3,
                "reference": "external-id/3",
                "language": "nl",
                "created_at": "2021-10-25T14:30:49.565775Z",
                "modified_at": "2021-10-25T14:30:49.565784Z"
            },
        ]
    }


MOCK_RESPONSE = MagicMock(
    status_code=200,
    json=json_data
)


@patch("surf.sitemap.requests.get", return_value=MOCK_RESPONSE)
@skipIf(settings.PROJECT == "nppo", "Site maps not supported by NPPO")
class TestSitemaps(TestCase):

    def test_index(self, request_get):
        """
        Checks validity of the starting point for scrapers
        """
        # Check format of the index
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html5lib")
        expected_locations = [
            "https://testserver/sitemap-main.xml",
            "https://testserver/sitemap-materials.xml",
            "https://testserver/sitemap-materials.xml?p=2",
        ]
        actual_locations = [location.text for location in soup.find_all("loc")]
        self.assertEqual(actual_locations, expected_locations)
        # Check that all links in sitemap are accessible
        for location in actual_locations:
            relative_url = location.replace("https://testserver", "")
            response = self.client.get(relative_url)
            self.assertEqual(response.status_code, 200)

    def test_materials_sitemap(self, request_get):
        """
        Checks whether correct information about materials gets passed to scrapers
        """
        response = self.client.get("/sitemap-materials.xml")
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html5lib")
        expected_locations = [
            "https://testserver/materialen/external-id:1",
            "https://testserver/en/materials/external-id.2",
            "https://testserver/materialen/external-id%2F3",
        ]
        expected_change_frequency = "daily"
        expected_modification_date = "2021-10-25"
        actual_urls = soup.find_all("url")
        self.assertEqual(len(actual_urls), len(expected_locations))
        for ix, url in enumerate(actual_urls):
            self.assertEqual(url.find("loc").text, expected_locations[ix])
            self.assertEqual(url.find("changefreq").text, expected_change_frequency)
            modification_date = url.find("lastmod")
            if ix == 2:
                self.assertIsNone(modification_date, "Expected created documents to not send out a modification date")
            else:
                self.assertEqual(modification_date.text, expected_modification_date)

    def test_main_sitemap(self, request_get):
        """
        Checks whether Edusources pages get passed on correctly (including the language variants)
        """
        response = self.client.get("/sitemap-main.xml")
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html5lib")
        expected_locations = [
            "https://testserver/",
            "https://testserver/hoe-werkt-het",
            "https://testserver/en",
            "https://testserver/en/how-does-it-work",
        ]
        expected_change_frequency = "monthly"
        actual_urls = soup.find_all("url")
        self.assertEqual(len(actual_urls), len(expected_locations))
        for ix, url in enumerate(actual_urls):
            location = url.find("loc").text
            self.assertEqual(location, expected_locations[ix])
            self.assertEqual(url.find("changefreq").text, expected_change_frequency)
            nl_link = url.find(attrs={"hreflang": "nl"})
            en_link = url.find(attrs={"hreflang": "en"})
            default_link = url.find(attrs={"hreflang": "x-default"})
            self.assertEqual(default_link["href"], nl_link["href"])
            self.assertNotEqual(default_link["href"], en_link["href"])
            self.assertIn(nl_link["href"], expected_locations)
            self.assertIn(en_link["href"], expected_locations)
