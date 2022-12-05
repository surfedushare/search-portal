from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from harvester.utils.extraction import get_harvest_seeds
from core.constants import Repositories
from sources.factories.hku.extraction import HkuMetadataResourceFactory, SET_SPECIFICATION


class TestGetHarvestSeedsHku(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.begin_of_time = make_aware(datetime(year=1970, month=1, day=1))
        HkuMetadataResourceFactory.create_common_responses()
        cls.seeds = get_harvest_seeds(Repositories.HKU, SET_SPECIFICATION, cls.begin_of_time)

    def test_get_record_state(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["state"], "active")
        self.assertEqual(seeds[10]["state"], "deleted")

    def test_get_id(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["external_id"], "hku:product:6247569")

    def test_get_files(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["files"], [
            {
                "mime_type": "application/pdf",
                "url": "https://octo.hku.nl/octo/repository/getfile?id=zZQC1ZBu8c4",
                "hash": "9ac373e877133f0c00173bd02d82b1861c9934a2",
                "title": "Budapest2005.pdf"
            }
        ])
        all_seeds = get_harvest_seeds(Repositories.HKU, SET_SPECIFICATION, self.begin_of_time, include_no_url=True)
        self.assertEqual(all_seeds[21]["files"], [])

    def test_get_url(self):
        seeds = self.seeds
        self.assertEqual(
            seeds[0]["url"],
            "https://octo.hku.nl/octo/repository/getfile?id=zZQC1ZBu8c4"
        )

    def test_get_mime_type(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["mime_type"], "application/pdf")

    def test_get_language(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["language"], {"metadata": "en"})
        self.assertEqual(seeds[10]["language"], {"metadata": "nl"})

    def test_get_title(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["title"], "Methodological Mapping")

    def test_get_description(self):
        seeds = self.seeds
        self.assertTrue(seeds[0]["description"].startswith("This symposium was brought to life"))

    def test_get_keywords(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["keywords"], [])
        self.assertEqual(
            seeds[2]["keywords"],
            [
                "crossovers", "didactische methoden", "makerschap", "performance", "touch", "interaction",
                "artistic research", "performance", "scenography", "fine arts"
            ]
        )

    def test_authors_property(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]['authors'], [
            {
                'name': 'Henk Slager', 'email': "henk.slager@hku.nl", 'external_id': None,
                'dai': None, 'orcid': None, 'isni': None
            },
        ])
        self.assertEqual(seeds[1]['authors'], [
            {
                'name': 'Henk Slager', 'email': None, 'external_id': None,
                'dai': None, 'orcid': None, 'isni': None
            },
        ])
        self.assertEqual(seeds[43]['authors'], [
            {
                'name': 'Eva den Heijer', 'email': "eva.denheijer@hku.nl", 'external_id': "hku:person:5952259",
                'dai': None, 'orcid': None, 'isni': None
            },
        ])

    def test_publisher_year(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["publisher_year"], 2005)
