from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from harvester.utils.extraction import get_harvest_seeds
from anatomy_tool.tests.factories import AnatomyToolOAIPMHFactory
from anatomy_tool.extraction import ANATOMY_TOOL_EXTRACTION_OBJECTIVE, AnatomyToolExtraction


class TestGetHarvestSeedsAnatomyTool(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        AnatomyToolOAIPMHFactory.create_common_anatomy_tool_responses()

    def extract_seed_types(self, seeds):
        normal = next(
            (seed for seed in seeds
             if seed["state"] != "deleted")
        )
        deleted = next(
            (seed for seed in seeds if seed["state"] == "deleted"), None
        )
        return {
            "normal": normal,
            "deleted": deleted,
        }

    def check_seed_integrity(self, seeds, include_deleted=True):
        # We'll check if seeds if various types are dicts with the same keys
        seed_types = self.extract_seed_types(seeds)
        for seed_type, seed in seed_types.items():
            if not include_deleted and seed_type == "deleted":
                assert seed is None, "Expected no deleted seeds"
                continue
            assert "state" in seed, "Missing key 'state' in seed"
            assert "external_id" in seed, "Missing key 'external_id' in seed"
            for required_key in ANATOMY_TOOL_EXTRACTION_OBJECTIVE.keys():
                assert required_key in seed, f"Missing key '{required_key}' in seed"
        # A deleted seed is special due to its "state"
        if include_deleted:
            self.assertEqual(seed_types["deleted"]["state"], "deleted")

    def test_get_complete_set(self):
        seeds = get_harvest_seeds("anatomy_tool", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(len(seeds), 10)
        self.check_seed_integrity(seeds)

    def test_get_complete_set_without_deletes(self):
        seeds = get_harvest_seeds("anatomy_tool", make_aware(datetime(year=1970, month=1, day=1)),
                                  include_deleted=False)
        self.assertEqual(len(seeds), 8)
        self.check_seed_integrity(seeds, include_deleted=False)

    def test_from_youtube_property(self):
        seeds = get_harvest_seeds("anatomy_tool", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(len(seeds), 10)
        youtube_seeds = [seed for seed in seeds if seed['from_youtube']]
        self.assertEqual(len(youtube_seeds), 0)

    def test_authors_property(self):
        self.skipTest("Needs implementation from Anatomy Tool")
        return
        seeds = get_harvest_seeds("anatomy_tool", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[0]['authors'], [
            {'name': 'O. Paul Gobée', 'email': None},
            {'name': 'Prof. X. Test', 'email': None}
        ])

    def test_analysis_allowed_property(self):
        seeds = get_harvest_seeds("anatomy_tool", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[0]['analysis_allowed'], True, "Expected standard material to allow analysis")
        self.assertEqual(seeds[6]['analysis_allowed'], False, "Expected restricted material to disallow analysis")

    def test_lom_educational_level(self):
        seeds = get_harvest_seeds("anatomy_tool", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[0]["lom_educational_levels"], ["HBO", "WO"])

    def test_get_files(self):
        seeds = get_harvest_seeds("anatomy_tool", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(len(seeds[0]["files"]), 1)
        file = seeds[0]["files"][0]
        self.assertEqual(file["mime_type"], "image/png")
        self.assertEqual(file["url"], "https://anatomytool.org/node/56055")
        self.assertEqual(file["title"], "URL 1")

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
            "invalid": None,
            None: None
        }
        for description, license in descriptions.items():
            self.assertEqual(AnatomyToolExtraction.parse_copyright_description(description), license)

    def test_get_copyright(self):
        seeds = get_harvest_seeds("anatomy_tool", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(len(seeds), 10, "Expected get_harvest_seeds to filter differently based on copyright")
        self.assertEqual(seeds[0]["copyright"], "cc-by-nc-sa-40")

    def test_get_technical_type(self):
        seeds = get_harvest_seeds("anatomy_tool", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[0]["technical_type"], "image")
