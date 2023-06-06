from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from harvester.utils.extraction import get_harvest_seeds
from core.constants import Repositories
from sources.factories.hva.extraction import HvaPureResourceFactory, SET_SPECIFICATION


class TestGetHarvestSeedsHva(TestCase):

    begin_of_time = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.begin_of_time = make_aware(datetime(year=1970, month=1, day=1))
        HvaPureResourceFactory.create_common_responses()
        cls.seeds = get_harvest_seeds(Repositories.HVA, SET_SPECIFICATION, cls.begin_of_time)

    def test_get_id(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["external_id"], "7288bd68-d62b-4db0-8cea-5f189e209254")

    def test_get_files(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["files"], [])
        self.assertEqual(seeds[3]["files"], [
            {
                "mime_type": "application/pdf",
                "url": "https://accpure.hva.nl/ws/api/research-outputs/d7126f6d-c412-43c8-ad2a-6acb7613917d/files/"
                       "MDIyMzRi/636835_schuldenvrij-de-weg-naar-werk_aangepast.pdf",
                "hash": "17c1945a55b6d00b0d17caed17762c94237e658d",
                "title": "636835_schuldenvrij-de-weg-naar-werk_aangepast.pdf",
                "copyright": None,
                "access_rights": "OpenAccess"
            }
        ])

    def test_get_url(self):
        seeds = self.seeds
        self.assertEqual(
            seeds[0]["url"],
            "https://accpure.hva.nl/en/publications/7288bd68-d62b-4db0-8cea-5f189e209254"
        )
        self.assertEqual(
            seeds[3]["url"],
            "https://accpure.hva.nl/ws/api/research-outputs/d7126f6d-c412-43c8-ad2a-6acb7613917d/files/MDIyMzRi/"
            "636835_schuldenvrij-de-weg-naar-werk_aangepast.pdf"
        )

    def test_get_mime_type(self):
        seeds = self.seeds
        self.assertIsNone(seeds[0]["mime_type"])
        self.assertEqual(seeds[3]["mime_type"], "application/pdf")

    def test_get_analysis_allowed(self):
        seeds = self.seeds
        self.assertFalse(seeds[0]["analysis_allowed"], "Expected closed-access to disallow analysis")
        self.assertTrue(seeds[3]["analysis_allowed"], "Expected open-access to allow analysis")

    def test_get_language(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["language"], {"metadata": "nl"})
        self.assertEqual(seeds[4]["language"], {"metadata": "en"})

    def test_get_title(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["title"], "Leerlingen in het Amsterdamse onderwijs")

    def test_get_description(self):
        seeds = self.seeds
        self.assertTrue(seeds[0]["description"].startswith("De relatie tussen schoolloopbanen van jongeren"))

    def test_keywords(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["keywords"], ['onderzoek', 'leerlingen', 'Amsterdam', 'schoolloopbanen', 'jongeren'])

    def test_authors_property(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]['authors'], [
            {'name': 'Ruben Fukkink', 'email': None, 'external_id': 140056, 'dai': None, 'orcid': None, 'isni': None},
            {'name': 'Sandra van Otterloo', 'email': None, 'external_id': 140057, 'dai': None, 'orcid': None, 'isni':
                None},
            {'name': 'Lotje Cohen', 'email': None, 'external_id': 140058, 'dai': None, 'orcid': None, 'isni': None},
            {'name': 'Merel van der Wouden', 'email': None, 'external_id': 140059, 'dai': None, 'orcid': None, 'isni':
                None},
            {'name': 'Bonne Zijlstra', 'email': None, 'external_id': 140060, 'dai': None, 'orcid': None, 'isni': None}
        ])

    def test_publisher_year(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["publisher_year"], 2016)

    def test_research_object_type(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["research_object_type"], "Report")

    def test_doi(self):
        seeds = self.seeds
        self.assertIsNone(seeds[0]["doi"])
        self.assertEqual(seeds[5]["doi"], "10.1088/0031-9120/50/5/573")
