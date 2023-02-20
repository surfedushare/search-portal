from datetime import datetime

from django.utils.timezone import make_aware

from harvester.utils.extraction import get_harvest_seeds
from core.constants import Repositories
from core.tests.base import SeedExtractionTestCase
from anatomy_tool.tests.factories import AnatomyToolOAIPMHFactory
from anatomy_tool.extraction import ANATOMY_TOOL_EXTRACTION_OBJECTIVE, AnatomyToolExtraction


class TestGetHarvestSeedsAnatomyTool(SeedExtractionTestCase):

    OBJECTIVE = ANATOMY_TOOL_EXTRACTION_OBJECTIVE

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        AnatomyToolOAIPMHFactory.create_common_anatomy_tool_responses()
        cls.begin_of_time = make_aware(datetime(year=1970, month=1, day=1))
        cls.set_spec = "anatomy_tool"
        cls.seeds = get_harvest_seeds(Repositories.ANATOMY_TOOL, cls.set_spec, cls.begin_of_time)

    def test_get_complete_set(self):
        seeds = self.seeds
        self.assertEqual(len(seeds), 10)
        self.check_seed_integrity(seeds, include_deleted=False)

    def test_get_complete_set_without_deletes(self):
        seeds = get_harvest_seeds(Repositories.ANATOMY_TOOL, self.set_spec, self.begin_of_time,
                                  include_deleted=False)
        self.assertEqual(len(seeds), 10)
        self.check_seed_integrity(seeds, include_deleted=False)

    def test_from_youtube_property(self):
        seeds = self.seeds
        self.assertEqual(len(seeds), 10)
        youtube_seeds = [seed for seed in seeds if seed['from_youtube']]
        self.assertEqual(len(youtube_seeds), 0)

    def test_authors_property(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]['authors'], [
            {'name': 'O. Paul Gobée', 'email': None, 'external_id': None, 'dai': None, 'orcid': None, 'isni': None},
            {'name': 'Prof. X. Test', 'email': None, 'external_id': None, 'dai': None, 'orcid': None, 'isni': None}
        ])

    def test_analysis_allowed_property(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]['analysis_allowed'], True, "Expected standard material to allow analysis")
        self.assertEqual(seeds[6]['analysis_allowed'], False, "Expected restricted material to disallow analysis")

    def test_lom_educational_level(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["lom_educational_levels"], ["HBO", "WO"])

    def test_get_files(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["files"], [
            {
                "mime_type": "image/png",
                "url": "https://anatomytool.org/node/56055",
                "hash": "2d49dee36ce2965cd9e03d91dbd4f9ac54de770a",
                "title": "URL 1",
                "copyright": "cc-by-nc-sa-40",
                "access_rights": "OpenAccess"
            }
        ])
        self.assertEqual(seeds[6]["files"], [
            {
                "mime_type": "image/jpeg",
                "url": "https://anatomytool.org/node/56176",
                "hash": "62c2493141fd745099b4b5a4d875c67d2103a964",
                "title": "URL 1",
                "copyright": "yes",
                "access_rights": "RestrictedAccess"
            }
        ])

    def test_parse_copyright_description(self):
        descriptions = {
            "http://creativecommons.org/licenses/by-nc-sa/3.0/nl/": "cc-by-nc-sa-30",
            "http://creativecommons.org/licenses/by-nc-sa/4.0/": "cc-by-nc-sa-40",
            "http://creativecommons.org/licenses/by-nc/4.0/": "cc-by-nc-40",
            "http://creativecommons.org/licenses/by-sa/3.0/nl/": "cc-by-sa-30",
            "http://creativecommons.org/licenses/by-sa/4.0/": "cc-by-sa-40",
            "http://creativecommons.org/licenses/by/3.0/nl/": "cc-by-30",
            "http://creativecommons.org/licenses/by/4.0/": "cc-by-40",
            "http://creativecommons.org/publicdomain/mark/1.0/": "pdm-10",
            "Public Domain": "pdm-10",
            "http://creativecommons.org/publicdomain/zero/1.0/": "cc0-10",
            "CC BY NC SA": "cc-by-nc-sa",
            "CC BY-NC-SA": "cc-by-nc-sa",
            "cc by": "cc-by",
            "Copyrighted": "yes",
            "invalid": None,
            None: None
        }
        for description, license in descriptions.items():
            self.assertEqual(AnatomyToolExtraction.parse_copyright_description(description), license)

    def test_get_copyright(self):
        seeds = self.seeds
        self.assertEqual(len(seeds), 10, "Expected get_harvest_seeds to filter differently based on copyright")
        self.assertEqual(seeds[0]["copyright"], "cc-by-nc-sa-40")
        self.assertEqual(seeds[6]["copyright"], "yes")

    def test_get_technical_type(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["technical_type"], "image")

    def test_get_keywords(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["keywords"], ['A05.6.02.001 Duodenum', 'A05.9.01.001 Pancreas'])

    def test_get_publisher_year(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["publisher_year"], 2016)
        self.assertIsNone(seeds[1]["publisher_year"])
