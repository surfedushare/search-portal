from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from harvester.utils.extraction import get_harvest_seeds
from core.constants import Repositories
from sources.factories.han.extraction import HanOAIPMHFactory, SET_SPECIFICATION


class TestGetHarvestSeedsHan(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.begin_of_time = make_aware(datetime(year=1970, month=1, day=1))
        HanOAIPMHFactory.create_common_responses()
        cls.seeds = get_harvest_seeds(Repositories.HAN, SET_SPECIFICATION, cls.begin_of_time)

    def test_get_id(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["external_id"], "oai:repository.han.nl:20.500.12470/7")
        self.assertEqual(seeds[2]["external_id"], "oai:repository.han.nl:20.500.12470/9",
                         "Expected deleted record to return an id")

    def test_get_files(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["files"], [
            {
                "mime_type": "application/pdf",
                "url": "https://repository.han.nl/han/bitstream/handle/20.500.12470/7/"
                       "A-artikel_Webcare_en_reputatieschade.pdf",
                "hash": "dfe656e9bdb0c1597ec44a74be46ac7eaa2dce3c",
                "title": "Attachment 1",
                "copyright": None,
                "access_rights": "OpenAccess"
            },
            {
                "mime_type": "text/html",
                "url": "http://hdl.handle.net/20.500.12470/7",
                "hash": "3f679086acfed2dddbb549dc24def669f59793ed",
                "title": "URL 1",
                "copyright": None,
                "access_rights": "OpenAccess"
            }
        ])
        self.assertEqual(seeds[2]["files"], [], "Expected deleted record to have no files")

    def test_get_url(self):
        seeds = self.seeds
        self.assertEqual(
            seeds[0]["url"],
            "https://repository.han.nl/han/bitstream/handle/20.500.12470/7/A-artikel_Webcare_en_reputatieschade.pdf"
        )
        self.assertIsNone(seeds[2]["url"], "Expected deleted record to have no url")

    def test_get_mime_type(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["mime_type"], "application/pdf")
        self.assertIsNone(seeds[2]["mime_type"], "Expected deleted record to have no mime_type")

    def test_get_language(self):
        self.skipTest("Not implemented yet, but seems essential for the system to function")

    def test_get_title(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["title"], "'Dat kan beter, ja...' : Webcare en het voorkomen van reputatieschade")
        self.assertIsNone(seeds[2]["title"], "Expected deleted record to have no title")

    def test_get_description(self):
        seeds = self.seeds
        self.assertTrue(seeds[0]["description"].startswith("Klanten uiten op social media"))
        self.assertIsNone(seeds[2]["description"], "Expected deleted record to have no description")

    def test_authors_property(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]['authors'], [
            {'name': 'R.G. van Os', 'email': None, 'external_id': None, 'dai': None, 'orcid': None, 'isni': None},
            {'name': 'Daphne Hachmang', 'email': None, 'external_id': None, 'dai': None, 'orcid': None, 'isni': None},
        ])
        self.assertEqual(seeds[2]["authors"], [], "Expected deleted record to have no authors")

    def test_publisher_year(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["publisher_year"], 2018)
        self.assertIsNone(seeds[2]["publisher_year"], "Expected deleted record to have no publisher_year")

    def test_research_object_type(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["research_object_type"], "info:eu-repo/semantics/article")
        self.assertIsNone(seeds[2]["research_object_type"], "Expected deleted record to have no research_object_type")

    def test_get_doi(self):
        seeds = self.seeds
        self.assertIsNone(seeds[0]["doi"], "DOI might not be specified")
        self.assertEqual(seeds[1]["doi"], "https://doi.org/10.18352/jsi.546")
        self.assertIsNone(seeds[2]["doi"], "Expected deleted record to have no doi")
