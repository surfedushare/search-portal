from django.test import TestCase


class SeedExtractionTestCase(TestCase):

    OBJECTIVE = {}

    set_spec = None
    begin_of_time = None

    def extract_seed_types(self, seeds):
        normal = next(
            (seed for seed in seeds
             if seed["state"] == "active")
        )
        deleted = next(
            (seed for seed in seeds if seed["state"] in ["inactive", "deleted"]), None
        )
        return {
            "normal": normal,
            "deleted": deleted,
        }

    def check_seed_integrity(self, seeds, include_deleted=True):
        # We'll check if seeds if various types are dicts with the same keys
        seed_types = self.extract_seed_types(seeds)
        for seed_type, seed in seed_types.items():
            if not include_deleted and seed_type in ["deleted", "inactive"]:
                assert seed is None, "Expected no deleted/inactive seeds"
                continue
            assert "state" in seed, "Missing key 'state' in seed"
            assert "external_id" in seed, "Missing key 'external_id' in seed"
            for required_key in self.OBJECTIVE.keys():
                assert required_key.replace("#", "") in seed, f"Missing key '{required_key}' in seed"
        # A deleted seed is special due to its "state"
        if include_deleted:
            self.assertIn(seed_types["deleted"]["state"], ["deleted", "inactive"])
