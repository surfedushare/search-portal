from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from harvester.utils.extraction import get_harvest_seeds
from core.constants import Repositories
from sources.factories.buas.extraction import BuasPureResourceFactory, SET_SPECIFICATION


class TestGetHarvestSeedsBuas(TestCase):

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
                "hash": "d42e0d5475f052d4fa0ef5216fd7dcbfc3a4374d"
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

    def test_get_copyright(self):
        seeds = self.seeds
        self.assertEqual(len(seeds), 20)
        self.assertEqual(seeds[0]["copyright"], "yes")
        self.assertEqual(seeds[1]["copyright"], "open-access")
        self.assertEqual(seeds[3]["copyright"], "open-access")
        seeds = get_harvest_seeds(Repositories.BUAS, SET_SPECIFICATION, self.begin_of_time, include_deleted=False)
        self.assertEqual(len(seeds), 19, "Expected get_harvest_seeds to delete invalid copyright")
        self.assertEqual(seeds[0]["copyright"], "open-access")

    def test_get_language(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["language"], "en")
        self.assertEqual(seeds[4]["language"], "en")

    def test_get_title(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["title"], "Edinburgh inspiring capital : ensuring world beats a path to our doors")

    def test_authors_property(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]['authors'], [
            {'name': 'KJ Dinnie', 'email': None, 'external_id': 28956, 'dai': None, 'orcid': None, 'isni': None}
        ])

    def test_publisher_year(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["publisher_year"], 2012)

    def test_research_object_type(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["research_object_type"], "Article")
