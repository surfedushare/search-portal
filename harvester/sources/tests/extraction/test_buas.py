from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from harvester.utils.extraction import get_harvest_seeds
from core.constants import Repositories
from sources.factories.buas.extraction import BuasPureResourceFactory, SET_SPECIFICATION


class TestGetHarvestSeedsBuas(TestCase):

    begin_of_time = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.begin_of_time = make_aware(datetime(year=1970, month=1, day=1))
        BuasPureResourceFactory.create_common_responses()
        cls.seeds = get_harvest_seeds(Repositories.BUAS, SET_SPECIFICATION, cls.begin_of_time)

    def test_get_id(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["external_id"], "b7b17301-7123-4113-aa8a-8391aa9d7e01")

    def test_get_files(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["files"], [])
        self.assertEqual(seeds[1]["files"], [
            {
                "title": None,
                "url": "http://www.control-online.nl/gamesindustrie/2010/04/26/nieuw-column-op-maandag/",
                "mime_type": "text/html",
                "hash": "d42e0d5475f052d4fa0ef5216fd7dcbfc3a4374d",
                "copyright": None,
                "access_rights": "OpenAccess"
            }
        ])
        self.assertEqual(seeds[3]["files"], [
            {
                "title": "Peeters_tourismandclimatemitigation_peetersp_ed_nhtv2007.pdf",
                "url": "https://pure.buas.nl/ws/files/15672869/"
                       "Peeters_tourismandclimatemitigation_peetersp_ed_nhtv2007.pdf",
                "mime_type": "application/pdf",
                "hash": "f8839eeea39968549dafe4075232074a15adcb63",
                "copyright": None,
                "access_rights": "OpenAccess"
            }
        ])

    def test_get_url(self):
        seeds = self.seeds
        self.assertEqual(
            seeds[0]["url"],
            "https://pure.buas.nl/en/publications/b7b17301-7123-4113-aa8a-8391aa9d7e01"
        )
        self.assertEqual(
            seeds[1]["url"],
            "http://www.control-online.nl/gamesindustrie/2010/04/26/nieuw-column-op-maandag/"
        )

    def test_get_mime_type(self):
        seeds = self.seeds
        self.assertIsNone(seeds[0]["mime_type"])
        self.assertEqual(seeds[1]["mime_type"], "text/html")

    def test_get_analysis_allowed(self):
        seeds = self.seeds
        self.assertFalse(seeds[0]["analysis_allowed"])
        self.assertTrue(seeds[1]["analysis_allowed"])

    def test_get_language(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["language"], {"metadata": "en"})
        self.assertEqual(seeds[4]["language"], {"metadata": "en"})

    def test_get_title(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["title"], "Edinburgh inspiring capital : ensuring world beats a path to our doors")

    def test_get_description(self):
        seeds = self.seeds
        self.assertEqual(
            seeds[0]["description"],
            "<p>Edinburgh inspiring capital : ensuring world beats a path to our doors</p>"
        )
        self.assertIsNone(seeds[1]["description"])

    def test_get_keywords(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["keywords"], [
            "inspiring capital",
            "beat the world",
        ])
        self.assertEqual(seeds[1]["keywords"], [])

    def test_authors_property(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]['authors'], [
            {
                'name': 'KJ Dinnie', 'email': None, 'external_id': '6f1bbf4a-b32a-4923-9f47-bb764f3dbbde',
                'dai': None, 'orcid': None, 'isni': None
            }
        ])

    def test_publisher_year(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["publisher_year"], 2012)

    def test_research_object_type(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["research_object_type"], "Article")
