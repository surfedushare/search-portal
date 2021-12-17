from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from harvester.utils.extraction import get_harvest_seeds
from edurep.tests.factories import EdurepOAIPMHFactory
from edurep.extraction import EDUREP_EXTRACTION_OBJECTIVE, EdurepDataExtraction


class TestGetHarvestSeedsEdurep(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        EdurepOAIPMHFactory.create_common_edurep_responses(include_delta=True)

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
            for required_key in EDUREP_EXTRACTION_OBJECTIVE.keys():
                assert required_key in seed, f"Missing key '{required_key}' in seed"
        # A deleted seed is special due to its "state"
        if include_deleted:
            self.assertEqual(seed_types["deleted"]["state"], "deleted")

    def test_get_complete_set(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(len(seeds), 17)
        self.check_seed_integrity(seeds)

    def test_get_partial_set(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=2020, month=2, day=10, hour=22, minute=22)))
        self.assertEqual(len(seeds), 6)
        self.check_seed_integrity(seeds)

    def test_get_complete_set_without_deletes(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)),
                                  include_deleted=False)
        self.assertEqual(len(seeds), 14)
        self.check_seed_integrity(seeds, include_deleted=False)

    def test_get_partial_set_without_deletes(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(
            datetime(year=2020, month=2, day=10, hour=22, minute=22)), include_deleted=False)
        self.assertEqual(len(seeds), 4)
        self.check_seed_integrity(seeds, include_deleted=False)

    def test_from_youtube_property(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(len(seeds), 17)
        youtube_seeds = [seed for seed in seeds if seed['from_youtube']]
        self.assertEqual(len(youtube_seeds), 8)

    def test_authors_property(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[3]['authors'], [
            {'name': 'Ruud Kok', 'email': None, 'external_id': None, 'dai': None, 'orcid': None}
        ])

    def test_publishers_property(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[3]['publishers'], ['AERES Hogeschool; HAS Hogeschool; Van Hall Larenstein'])
        self.assertEqual(seeds[5]['publishers'], ['SURFnet'])
        self.assertEqual(seeds[15]['publishers'], ['Erasmus Medisch Centrum'])

    def test_consortium_property(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[3]['consortium'], None)
        self.assertEqual(seeds[15]['consortium'], 'HBO Verpleegkunde')

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

    def test_lom_educational_level(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[0]["lom_educational_levels"], [],
                         "Expected deleted materials to have no educational level")
        self.assertEqual(seeds[1]["lom_educational_levels"], ["HBO"],
                         "Expected HBO materials to have an educational level")
        self.assertEqual(seeds[2]["lom_educational_levels"], ["WO"],
                         "Expected HBO materials to have an educational level")

    def test_lowest_educational_level(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[0]["lowest_educational_level"], -1,
                         "Expected deleted materials to have negative educational level")
        self.assertEqual(seeds[1]["lowest_educational_level"], 2,
                         "Expected HBO materials to have an educational level of 2")
        self.assertEqual(seeds[2]["lowest_educational_level"], 3,
                         "Expected HBO materials to have an educational level of 3")

    def test_get_files(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[0]["files"], [], "Expected deleted material to have no files")
        self.assertEqual(len(seeds[1]["files"]), 1)
        file = seeds[1]["files"][0]
        self.assertEqual(file["mime_type"], "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        self.assertEqual(file["url"], "https://surfsharekit.nl/objectstore/182216be-31a2-43c3-b7de-e5dd355b09f7")
        self.assertEqual(file["hash"], "0ed38cdc914e5e8a6aa1248438a1e2032a14b0de")
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
            "http://creativecommons.org/publicdomain/zero/1.0/": "cc0-10",
            "CC BY NC SA": "cc-by-nc-sa",
            "CC BY-NC-SA": "cc-by-nc-sa",
            "cc by": "cc-by",
            "invalid": None,
            None: None
        }
        for description, license in descriptions.items():
            self.assertEqual(EdurepDataExtraction.parse_copyright_description(description), license)

    def test_get_copyright(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(len(seeds), 17, "Expected get_harvest_seeds to filter differently based on copyright")
        self.assertEqual(seeds[1]["copyright"], "cc-by-nc-40",
                         "Expected 'yes' copyright to look at copyright_description")
        self.assertEqual(seeds[2]["copyright"], "cc-by-40",
                         "Expected copyright to be present even though copyright_description is missing")

    def test_get_technical_type(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertIsNone(seeds[0]["technical_type"], "Expected deleted material to have unknown technical type")
        self.assertEqual(seeds[1]["technical_type"], "document",
                         "Expected technical type to be deferred from mime type")
        self.assertEqual(seeds[2]["technical_type"], "unknown",
                         "Expected unknown technical type when mime type is unknown")

    def test_get_material_types(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertEqual(seeds[0]["material_types"], [],
                         "Expected deleted material to have no material types")
        self.assertEqual(seeds[1]["material_types"], [],
                         "Expected material without a type to return empty list")
        self.assertEqual(seeds[4]["material_types"], ["weblecture"])

    def test_get_publisher_year(self):
        seeds = get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
        self.assertIsNone(seeds[0]["publisher_year"], "Expected deleted material to have no publication year")
        self.assertIsNone(seeds[1]["publisher_year"],
                          "Expected material without publication date to have no publication year")
        self.assertEqual(seeds[3]["publisher_year"], 2017)
