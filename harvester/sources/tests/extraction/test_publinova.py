from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from harvester.utils.extraction import get_harvest_seeds
from core.constants import Repositories
from sources.factories.publinova.extraction import PublinovaMetadataResourceFactory, SET_SPECIFICATION


class TestGetHarvestSeedsPublinova(TestCase):

    begin_of_time = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.begin_of_time = make_aware(datetime(year=1970, month=1, day=1))
        PublinovaMetadataResourceFactory.create_common_responses()
        cls.seeds = get_harvest_seeds(Repositories.PUBLINOVA, SET_SPECIFICATION, cls.begin_of_time, include_no_url=True)

    def test_get_record_state(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["state"], "active")

    def test_get_id(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["external_id"], "0bd5a2c2-5621-454a-8a4e-f48d4d1c59ea")

    def test_get_files(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["files"], [])
        self.assertEqual(seeds[1]["files"], [
            {
                "mime_type": "application/pdf",
                "url": "https://api.publinova.acc.surf.zooma.cloud/api/products/"
                       "191ba2b9-da90-4c11-aa1e-0b221c6e2d42/download/184e5d6e-8bec-42dc-9a4d-034b27b9fad9",
                "hash": "805592bebcba0d98795fca7792c2d9c3fb33218b",
                "title": "Test-document-SP.pdf"
            }
        ])

    def test_get_url(self):
        seeds = self.seeds
        self.assertIsNone(seeds[0]["url"])
        self.assertEqual(
            seeds[1]["url"],
            "https://api.publinova.acc.surf.zooma.cloud/api/products/"
            "191ba2b9-da90-4c11-aa1e-0b221c6e2d42/download/184e5d6e-8bec-42dc-9a4d-034b27b9fad9"
        )

    def test_get_mime_type(self):
        seeds = self.seeds
        self.assertIsNone(seeds[0]["mime_type"])
        self.assertEqual(seeds[1]["mime_type"], "application/pdf")

    def test_get_technical_type(self):
        seeds = self.seeds
        self.assertIsNone(seeds[0]["technical_type"])
        self.assertEqual(seeds[1]["technical_type"], "document")

    def test_analysis_allowed(self):
        seeds = self.seeds
        self.assertTrue(seeds[0]["analysis_allowed"])
        self.assertFalse(seeds[2]["analysis_allowed"])

    # def test_get_language(self):
    #     seeds = self.seeds
    #     self.assertEqual(seeds[0]["language"], {"metadata": "en"})
    #     self.assertEqual(seeds[10]["language"], {"metadata": "nl"})

    def test_get_keywords(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["keywords"], [])
        self.assertEqual(seeds[5]["keywords"], ["<script>alert('keyword script');</script>"])

    def test_authors_property(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]['authors'], [
            {
                'name': 'Steef Beef', 'email': "steef-beef@radicalen.nl",
                'external_id': "c9991f99-e69f-4c82-a79f-f97e21ea3d73", 'dai': None, 'orcid': None, 'isni': None
            },
        ])
        self.assertEqual(seeds[10]['authors'], [])

    # def test_publisher_year(self):
    #     seeds = self.seeds
    #     self.assertEqual(seeds[0]["publisher_year"], 2005)
