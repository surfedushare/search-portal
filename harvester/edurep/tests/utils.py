from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from edurep.utils import get_edurep_oaipmh_seeds, EDUREP_EXTRACTION_OBJECTIVE


class TestGetEdurepOAIPMHSeeds(TestCase):

    fixtures = ["surf-oaipmh-1970-01-01", "surf-oaipmh-2020-01-01"]

    def extract_seed_types(self, seeds):
        normal = next(
            (seed for seed in seeds
             if seed["state"] != "deleted" and "maken.wikiwijs.nl" not in seed["url"])
        )
        deleted = next(
            (seed for seed in seeds if seed["state"] == "deleted"), None
        )
        # imscp = next(
        #     (seed for seed in seeds if seed["url"] and "maken.wikiwijs.nl" in seed["url"]), None
        # )
        return {
            "normal": normal,
            "deleted": deleted,
            # "imscp": imscp
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
        # IMSCP seeds are special due to their adjusted URL's
        # TODO: fix this, currently SURF can contain Wikiwijsmaken materials that don't support IMSCP interface
        # self.assertIn("package_url", seed_types["imscp"])
        # self.assertTrue(seed_types["imscp"]["url"].endswith("?imscp"))

    def test_get_complete_set(self):
        seeds = get_edurep_oaipmh_seeds("surf", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(len(seeds), 13)
        self.check_seed_integrity(seeds)

    def test_get_partial_set(self):
        seeds = get_edurep_oaipmh_seeds("surf", make_aware(datetime(year=2020, month=2, day=10, hour=22, minute=22)))
        self.assertEqual(len(seeds), 6)
        self.check_seed_integrity(seeds)

    def test_get_complete_set_without_deletes(self):
        seeds = get_edurep_oaipmh_seeds("surf", make_aware(datetime(year=1970, month=1, day=1)), include_deleted=False)
        self.assertEqual(len(seeds), 10)
        self.check_seed_integrity(seeds, include_deleted=False)

    def test_get_partial_set_without_deletes(self):
        seeds = get_edurep_oaipmh_seeds("surf", make_aware(
            datetime(year=2020, month=2, day=10, hour=22, minute=22)), include_deleted=False)
        self.assertEqual(len(seeds), 4)
        self.check_seed_integrity(seeds, include_deleted=False)

    def test_from_youtube_property(self):
        seeds = get_edurep_oaipmh_seeds("surf", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(len(seeds), 13)
        youtube_seeds = [seed for seed in seeds if seed['from_youtube']]
        self.assertEqual(len(youtube_seeds), 3)

    def test_publishers_output(self):
        seeds = get_edurep_oaipmh_seeds("surf", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[3]['publishers'], ['AERES Hogeschool', 'HAS Hogeschool', 'Van Hall Larenstein'])
        self.assertEqual(seeds[5]['publishers'], ['Hanze Hogeschool'])
