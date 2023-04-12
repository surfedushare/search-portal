from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from harvester.utils.extraction import get_harvest_seeds
from core.constants import Repositories
from sources.factories.hku.extraction import HkuMetadataResourceFactory, SET_SPECIFICATION


class TestGetHarvestSeedsHku(TestCase):

    begin_of_time = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.begin_of_time = make_aware(datetime(year=1970, month=1, day=1))
        HkuMetadataResourceFactory.create_common_responses()
        cls.seeds = get_harvest_seeds(Repositories.HKU, SET_SPECIFICATION, cls.begin_of_time)

    def test_get_record_state(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["state"], "active")
        self.assertEqual(seeds[8]["state"], "deleted")

    def test_get_id(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["external_id"], "hku:product:5951952")

    def test_get_files(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["files"], [
            {
                "title": "HKU_lectoraat_Play_Design_Development_Nuffic_Living_Lab_model_2014.mp4",
                "url": "https://octo.hku.nl/octo/repository/getfile?id=xRjq_aC4sKU",
                "mime_type": "application/pdf",
                "hash": "3bb6b2c5cb318b7daa677e51095084c45209ae2f",
                "copyright": "cc-by-nc-nd-40",
                "access_rights": "OpenAccess"
            }

        ])
        self.assertEqual(len(seeds), 9, "Expected documents without URL to get excluded")
        all_seeds = get_harvest_seeds(Repositories.HKU, SET_SPECIFICATION, self.begin_of_time, include_no_url=True)
        self.assertEqual(len(all_seeds), 10)
        self.assertEqual(all_seeds[7]["files"], [], "Expected no files to show as an empty list")

    def test_get_copyright(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["copyright"], "cc-by-nc-nd-40")

    def test_get_url(self):
        seeds = self.seeds
        self.assertEqual(
            seeds[0]["url"],
            "https://octo.hku.nl/octo/repository/getfile?id=xRjq_aC4sKU"
        )

    def test_get_mime_type(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["mime_type"], "application/pdf")

    def test_get_language(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["language"], {"metadata": "en"})
        self.assertEqual(seeds[4]["language"], {"metadata": "nl"})

    def test_get_title(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["title"], "Nuffic Living Lab: a trailer for an international collaboration model")

    def test_get_description(self):
        seeds = self.seeds
        self.assertTrue(seeds[0]["description"].startswith("Based upon years of experience of working in quadruple"))

    def test_get_keywords(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["keywords"], [])
        self.assertEqual(
            seeds[1]["keywords"],
            [
                "HKU", "Play Design and Development", "Applied Games", "Serious Games", "Gamification", "Game Design",
                "Architecture", "Vitrivius", "Game Development", "Design Principles", "Mental Healthcare", "Moodbot"
            ]
        )

    def test_authors_property(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]['authors'], [], "Expected documents without persons to have no authors")
        self.assertEqual(seeds[1]['authors'], [
            {
                "name": "Liesbet van Roes", "email": None, "external_id": "hku:person:6699976",
                "dai": None, "orcid": None, "isni": None
            },
            {
                "name": "Mic Haring", "email": "mic.haring@hku.nl", "external_id": "hku:person:6699827",
                "dai": None, "orcid": None, "isni": None
            }
        ])
        self.assertEqual(seeds[2]['authors'], [
            {
                "name": "Ketels", "email": "n.ketels@hku.nl", "external_id": "hku:person:6699884",
                "dai": None, "orcid": None, "isni": None
            }

        ])

    def test_publisher_year(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["publisher_year"], 2014)
