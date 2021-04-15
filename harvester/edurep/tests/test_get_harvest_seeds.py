from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from harvester.utils.extraction import get_harvest_seeds
from edurep.tests.factories import EdurepOAIPMHFactory
from edurep.extraction import EDUREP_EXTRACTION_OBJECTIVE


class TestGetHarvestSeedsEdurep(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        EdurepOAIPMHFactory.create_common_edurep_responses(include_delta=True)

    def extract_seed_types(self, seeds):
        normal = next(
            (seed for seed in seeds
             if seed["state"] != "deleted" and "maken.wikiwijs.nl" not in seed["url"])
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
            for required_key in EDUREP_EXTRACTION_OBJECTIVE.keys():
                assert required_key in seed, f"Missing key '{required_key}' in seed"
        # A deleted seed is special due to its "state"
        if include_deleted:
            self.assertEqual(seed_types["deleted"]["state"], "deleted")

    def test_get_complete_set(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(len(seeds), 18)
        self.check_seed_integrity(seeds)

    def test_get_partial_set(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=2020, month=2, day=10, hour=22, minute=22)))
        self.assertEqual(len(seeds), 6)
        self.check_seed_integrity(seeds)

    def test_get_complete_set_without_deletes(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)),
                                  include_deleted=False)
        self.assertEqual(len(seeds), 15)
        self.check_seed_integrity(seeds, include_deleted=False)

    def test_get_partial_set_without_deletes(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(
            datetime(year=2020, month=2, day=10, hour=22, minute=22)), include_deleted=False)
        self.assertEqual(len(seeds), 4)
        self.check_seed_integrity(seeds, include_deleted=False)

    def test_from_youtube_property(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(len(seeds), 18)
        youtube_seeds = [seed for seed in seeds if seed['from_youtube']]
        self.assertEqual(len(youtube_seeds), 8)

    def test_authors_property(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[3]['authors'], ['Ruud Kok'])

    def test_publishers_property(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[3]['publishers'], ['AERES Hogeschool; HAS Hogeschool; Van Hall Larenstein'])
        self.assertEqual(seeds[5]['publishers'], ['SURFnet'])

    def test_is_restricted(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[0]['is_restricted'], False, "Expected deleted material to have no restriction")
        self.assertEqual(seeds[1]['is_restricted'], False, "Expected standard material to have no restriction")
        self.assertEqual(seeds[8]['is_restricted'], True, "Expected restricted material to indicate restriction")

    def test_analysis_allowed_property(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[0]['analysis_allowed'], False, "Expected deleted material to disallow analysis")
        self.assertEqual(seeds[1]['analysis_allowed'], True, "Expected standard material to allow analysis")
        self.assertEqual(seeds[8]['analysis_allowed'], False, "Expected restricted material to disallow analysis")
        self.assertEqual(seeds[15]['analysis_allowed'], False, "Expected nd copyright material to disallow analysis")

    def test_is_part_of_property(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[0]['is_part_of'], None, "Expected deleted material to be part of nothing")
        self.assertEqual(seeds[1]['is_part_of'], None, "Expected standard material to have no parent")
        self.assertEqual(seeds[4]['is_part_of'], None, "Expected parent material to have no parent")
        self.assertEqual(
            seeds[5]['is_part_of'],
            "surfsharekit:oai:surfsharekit.nl:3c2b4e81-e9a1-41bc-8b6a-97bfe7e4048b",
            "Expected child material to specify its parent"
        )

    def test_has_parts_property(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[0]['has_parts'], [], "Expected deleted material to have no parts")
        self.assertEqual(seeds[1]['has_parts'], [], "Expected standard material to have no parts")
        self.assertEqual(
            seeds[4]['has_parts'],
            [
                "surfsharekit:oai:surfsharekit.nl:a18cdda7-e9c7-40d7-a7ad-6e875d9015ce",
                "surfsharekit:oai:surfsharekit.nl:8936d0a3-4157-45f4-9595-c26d4c029d97",
                "surfsharekit:oai:surfsharekit.nl:f929b625-5ef7-47b8-8fa8-94c969d0c427",
                "surfsharekit:oai:surfsharekit.nl:befb515c-5dce-4f27-82a4-2f5a7a3618a4"
            ],
            "Expected parent material to have children and specify the external ids"
        )
        self.assertEqual(seeds[5]['has_parts'], [], "Expected child material to have no children")

    def test_ideas_property(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[0]["ideas"], [], "Expected deleted material to return no idea data")
        possible_ideas = [
            "Informatievaardigheid vocabulaire 2020",
            "Publiceren en communiceren",
            "Publiceren (van eindproduct)"
        ]
        self.assertTrue(seeds[1]["ideas"])
        for idea in seeds[1]["ideas"]:
            self.assertIn(idea, possible_ideas, "Expected material with idea elements to return the spliced strings")
        self.assertEqual(seeds[2]["ideas"], [], "Expected material without ideas to return empty list")
        self.assertEqual(seeds[3]["ideas"], [], "Expected material from other than Sharekit to ignore ideas")
