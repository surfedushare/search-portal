from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from harvester.utils.extraction import get_harvest_seeds
from core.constants import Repositories
from sources.factories.greeni.extraction import GreeniOAIPMHResourceFactory, SET_SPECIFICATION


class TestGetHarvestSeedsGreeni(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.begin_of_time = make_aware(datetime(year=1970, month=1, day=1))
        GreeniOAIPMHResourceFactory.create_common_responses()
        cls.seeds = get_harvest_seeds(Repositories.GREENI, SET_SPECIFICATION, cls.begin_of_time)

    def test_get_id(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["external_id"], "oai:www.greeni.nl:VBS:2:121587")

    def test_get_files(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["files"], [
            {
                "mime_type": "application/pdf",
                "url": "https://www.greeni.nl/iguana/CMS.MetaDataEditDownload.cls?file=2:121587:1",
                "hash": "c75306b29041ba822c5310eb19d8582a9b07a585",
                "title": "CMS.MetaDataEditDownload.cls?file=2:121587:1"
            },
            {
                "mime_type": "text/html",
                "url": "https://www.greeni.nl/iguana/www.main.cls?surl=greenisearch#RecordId=2.121587",
                "hash": "78570277381005bbbe9fff97c58bb4272aa18609",
                "title": "www.main.cls?surl=greenisearch#RecordId=2.121587"
            }
        ])

    def test_get_url(self):
        seeds = self.seeds
        self.assertEqual(
            seeds[0]["url"],
            "https://www.greeni.nl/iguana/CMS.MetaDataEditDownload.cls?file=2:121587:1"
        )

    def test_get_mime_type(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["mime_type"], "application/pdf")
        self.assertIsNone(seeds[1]["mime_type"])

    def test_get_language(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["language"], "nl")
        self.assertEqual(seeds[30]["language"], "en")

    def test_get_copyright(self):
        seeds = self.seeds
        self.assertEqual(len(seeds), 100, "Expected get_harvest_seeds to filter differently based on copyright")
        self.assertEqual(seeds[0]["copyright"], "open-access")
        self.assertEqual(seeds[1]["copyright"], "yes")
        seeds = get_harvest_seeds(Repositories.GREENI, SET_SPECIFICATION, self.begin_of_time, include_deleted=False)
        self.assertEqual(len(seeds), 97, "Expected get_harvest_seeds to delete invalid copyright")
        self.assertEqual(seeds[1]["copyright"], "open-access")

    def test_get_title(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["title"], "Out of the box...!")

    def test_get_description(self):
        seeds = self.seeds
        self.assertTrue(seeds[0]["description"].startswith("Hoe kunnen de krachten gebundeld worden"))

    def test_authors_property(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]['authors'], [
            {'name': 'W. Timmermans', 'email': None, 'external_id': None, 'dai': None, 'orcid': None, 'isni': None},
            {'name': 'J. Jonkhof', 'email': None, 'external_id': None, 'dai': None, 'orcid': None, 'isni': None},
        ])

    def test_get_publishers(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["publishers"], ["VHL"])
        self.assertEqual(seeds[9]["publishers"], ["Agrimedia"])

    def test_publisher_year(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["publisher_year"], 2010)
        self.assertEqual(seeds[1]["publisher_year"], 2012)
        self.assertIsNone(seeds[2]["publisher_year"], "Expected parse errors to be ignored")

    def test_research_object_type(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["research_object_type"], "info:eu-repo/semantics/book")
        self.assertIsNone(seeds[1]["research_object_type"])

    def test_get_doi(self):
        seeds = self.seeds
        self.assertIsNone(seeds[0]["doi"], "DOI might not be specified")
        self.assertEqual(seeds[3]["doi"], "doi:10.31715/2018.6")
