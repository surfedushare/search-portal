from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from harvester.utils.extraction import get_harvest_seeds
from core.constants import Repositories
from sharekit.tests.factories import SharekitMetadataHarvestFactory
from sharekit.extraction import SHAREKIT_EXTRACTION_OBJECTIVE


class TestGetHarvestSeedsSharekit(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.set_spec = "edusources"
        cls.begin_of_time = make_aware(datetime(year=1970, month=1, day=1))
        SharekitMetadataHarvestFactory.create_common_sharekit_responses(include_delta=True)

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
            for required_key in SHAREKIT_EXTRACTION_OBJECTIVE.keys():
                assert required_key.replace("#", "") in seed, f"Missing key '{required_key}' in seed"
        # A deleted seed is special due to its "state"
        if include_deleted:
            self.assertEqual(seed_types["deleted"]["state"], "deleted")

    def test_get_complete_set(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, self.begin_of_time)
        self.assertEqual(len(seeds), 16)
        self.check_seed_integrity(seeds)

    def test_get_partial_set(self):
        seeds = get_harvest_seeds(
            Repositories.SHAREKIT,
            self.set_spec,
            make_aware(datetime(year=2020, month=2, day=9, hour=22, minute=22))
        )
        self.assertEqual(len(seeds), 5)
        self.check_seed_integrity(seeds)

    def test_get_complete_set_without_deletes(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, self.begin_of_time,
                                  include_deleted=False)
        self.assertEqual(len(seeds), 14)
        self.check_seed_integrity(seeds, include_deleted=False)

    def test_get_partial_set_without_deletes(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, make_aware(
            datetime(year=2020, month=2, day=9, hour=22, minute=22)), include_deleted=False)
        self.assertEqual(len(seeds), 4)
        self.check_seed_integrity(seeds, include_deleted=False)

    def test_from_youtube_property(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, self.begin_of_time)
        self.assertEqual(len(seeds), 16)
        youtube_seeds = [seed for seed in seeds if seed['from_youtube']]
        self.assertEqual(len(youtube_seeds), 9)

    def test_authors_property(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, self.begin_of_time)
        self.assertEqual(seeds[2]['authors'], [
            {
                'name': 'Ruud Kok',
                'email': 'Ruud Kok',
                'external_id': '83e7c163-075e-4eb2-8247-d975cf047dba',
                'dai': None,
                'orcid': None,
                'isni': None
            },
            {
                'name': 'Astrid Bulte',
                'email': 'Astrid Bulte',
                'external_id': '1174c1b9-f010-4a0a-98c0-2ceeefd0b506',
                'dai': None,
                'orcid': None,
                'isni': None
            },
            {
                'name': 'Hans Poorthuis',
                'email': 'Hans Poorthuis',
                'external_id': 'c0ab267a-ad56-480c-a13a-90b325f45b5d',
                'dai': None,
                'orcid': None,
                'isni': None
            },
        ])

    def test_publishers_property(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, self.begin_of_time)
        self.assertEqual(seeds[2]['publishers'], ['SURFnet'])
        self.assertEqual(seeds[4]['publishers'], ['SURFnet'])

    def test_is_restricted(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, self.begin_of_time)
        for seed in seeds:
            self.assertFalse(seed["is_restricted"])

    def test_analysis_allowed_property(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, self.begin_of_time)
        self.assertEqual(seeds[0]['analysis_allowed'], True, "Expected standard material to allow analysis")
        self.assertEqual(seeds[12]['analysis_allowed'], False, "Expexted nd copyright material to disallow analysis")
        self.assertEqual(seeds[13]['analysis_allowed'], False, "Expexted yes copyright material to disallow analysis")

    def test_is_part_of_property(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, self.begin_of_time)
        self.assertEqual(seeds[0]['is_part_of'], [], "Expected standard material to have no parent")
        self.assertEqual(
            seeds[4]['is_part_of'],
            ["3c2b4e81-e9a1-41bc-8b6a-97bfe7e4048b"],
            "Expected child material to specify its parent"
        )

    def test_has_parts_property(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, self.begin_of_time)
        self.assertEqual(seeds[0]['has_parts'], [], "Expected standard material to have no parts")
        self.assertEqual(
            seeds[3]['has_parts'],
            [
                "a18cdda7-e9c7-40d7-a7ad-6e875d9015ce",
                "8936d0a3-4157-45f4-9595-c26d4c029d97",
                "f929b625-5ef7-47b8-8fa8-94c969d0c427",
                "befb515c-5dce-4f27-82a4-2f5a7a3618a4"
            ],
            "Expected parent material to have children and specify the external ids"
        )
        self.assertEqual(seeds[5]['has_parts'], [], "Expected child material to have no children")

    def test_ideas_property(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, self.begin_of_time)
        possible_ideas = [
            "Informatievaardigheid vocabulaire 2020",
            "Publiceren en communiceren",
            "Publiceren (van eindproduct)"
        ]
        self.assertTrue(seeds[0]["ideas"])
        for idea in seeds[0]["ideas"]:
            self.assertIn(idea, possible_ideas, "Expected material with idea elements to return the spliced strings")
        self.assertEqual(seeds[2]["ideas"], [], "Expected material without ideas to return empty list")

    def test_lom_educational_level(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, self.begin_of_time)
        self.assertEqual(seeds[0]["lom_educational_levels"], ["HBO"],
                         "Expected HBO materials to have an educational level")
        self.assertEqual(seeds[1]["lom_educational_levels"], ["WO"],
                         "Expected HBO materials to have an educational level")

    def test_lowest_educational_level(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, self.begin_of_time)
        self.assertEqual(seeds[0]["lowest_educational_level"], 2,
                         "Expected HBO materials to have an educational level of 2")
        self.assertEqual(seeds[1]["lowest_educational_level"], 3,
                         "Expected HBO materials to have an educational level of 3")

    def test_get_files(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, self.begin_of_time)
        self.assertEqual(len(seeds[0]["files"]), 1)
        file = seeds[0]["files"][0]
        self.assertEqual(file["mime_type"], "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        self.assertEqual(file["url"], "https://surfsharekit.nl/objectstore/182216be-31a2-43c3-b7de-e5dd355b09f7")
        self.assertEqual(file["title"], "40. Exercises 5.docx")
        self.assertEqual(file["hash"], "0ed38cdc914e5e8a6aa1248438a1e2032a14b0de")
        for file in seeds[2]["files"]:
            self.assertTrue(file["mime_type"], "Mimetype should never be falsy")
            self.assertTrue(file["url"], "Links should never be falsy")
            self.assertTrue(file["title"], "Names should never be falsy")
            self.assertTrue(file["hash"], "Hashes should never be falsy")

    def test_get_technical_type(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, self.begin_of_time)
        self.assertEqual(seeds[0]["technical_type"], "document",
                         "Expected unknown technical types to be deferred from mime type")
        self.assertEqual(seeds[2]["technical_type"], "document",
                         "Expected files without URL and mime type to be ignored for technical_format")
        self.assertEqual(seeds[3]["technical_type"], "video", "Expected technicalFormat to be used when present")
        self.assertEqual(seeds[4]["technical_type"], "website", "Expected links to be a fallback if there are no files")
        self.assertEqual(seeds[5]["technical_type"], "unknown", "Expected 'unknown' for missing mime types")

    def test_get_material_types(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, self.begin_of_time)
        self.assertEqual(seeds[0]["material_types"], [], "Expected material without a type to return empty list")
        self.assertEqual(seeds[1]["material_types"], [], "Expected material with null as type to return empty list")
        self.assertEqual(seeds[3]["material_types"], ["kennisoverdracht"])
        self.assertEqual(seeds[4]["material_types"], ["kennisoverdracht"],
                         "Expected a single value to transform to a list")
        self.assertEqual(seeds[5]["material_types"], ["kennisoverdracht"],
                         "Expected null values to get filtered from lists")

    def test_get_publisher_year(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, self.set_spec, self.begin_of_time)
        self.assertEqual(seeds[0]["publisher_year"], 1970)
        self.assertIsNone(seeds[8]["publisher_year"], "Expected deleted material to have no publisher year")


class TestGetHarvestSeedsSharekitRestricted(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.set_spec = "edusourcesprivate"
        cls.begin_of_time = make_aware(datetime(year=1970, month=1, day=1))
        SharekitMetadataHarvestFactory.create_common_sharekit_responses(include_delta=True, is_restricted=True)

    def test_is_restricted(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, "edusourcesprivate", self.begin_of_time)
        for seed in seeds:
            self.assertTrue(seed["is_restricted"])

    def test_analysis_allowed_property(self):
        seeds = get_harvest_seeds(Repositories.SHAREKIT, "edusourcesprivate", self.begin_of_time)
        for seed in seeds:
            self.assertFalse(seed["analysis_allowed"])
