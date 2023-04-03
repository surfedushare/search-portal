from datetime import datetime

from django.utils.timezone import make_aware

from harvester.utils.extraction import get_harvest_seeds
from core.constants import Repositories
from core.tests.base import SeedExtractionTestCase
from edurep.tests.factories import EdurepOAIPMHFactory
from edurep.extraction import EDUREP_EXTRACTION_OBJECTIVE, EdurepDataExtraction


class TestGetHarvestSeedsEdurep(SeedExtractionTestCase):

    OBJECTIVE = EDUREP_EXTRACTION_OBJECTIVE

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.set_spec = "surfsharekit"
        cls.begin_of_time = make_aware(datetime(year=1970, month=1, day=1))
        EdurepOAIPMHFactory.create_common_edurep_responses(include_delta=True)
        cls.seeds = get_harvest_seeds(Repositories.EDUREP, cls.set_spec, cls.begin_of_time)

    def test_get_complete_set(self):
        seeds = self.seeds
        self.assertEqual(len(seeds), 17)
        self.check_seed_integrity(seeds)

    def test_get_partial_set(self):
        seeds = get_harvest_seeds(
            Repositories.EDUREP,
            self.set_spec,
            make_aware(datetime(year=2020, month=2, day=10, hour=22, minute=22))
        )
        self.assertEqual(len(seeds), 6)
        self.check_seed_integrity(seeds)

    def test_get_complete_set_without_deletes(self):
        seeds = get_harvest_seeds(Repositories.EDUREP, self.set_spec, self.begin_of_time, include_deleted=False)
        self.assertEqual(len(seeds), 9)
        self.check_seed_integrity(seeds, include_deleted=False)

    def test_get_partial_set_without_deletes(self):
        seeds = get_harvest_seeds(
            Repositories.EDUREP,
            self.set_spec,
            make_aware(datetime(year=2020, month=2, day=10, hour=22, minute=22)),
            include_deleted=False
        )
        self.assertEqual(len(seeds), 4)
        self.check_seed_integrity(seeds, include_deleted=False)

    def test_from_youtube_property(self):
        seeds = self.seeds
        self.assertEqual(len(seeds), 17)
        youtube_seeds = [seed for seed in seeds if seed['from_youtube']]
        self.assertEqual(len(youtube_seeds), 8)

    def test_authors_property(self):
        seeds = self.seeds
        self.assertEqual(seeds[3]['authors'], [
            {'name': 'Ruud Kok', 'email': None, 'external_id': None, 'dai': None, 'orcid': None, 'isni': None}
        ])

    def test_organizations_property(self):
        seeds = self.seeds
        self.assertIsNone(seeds[0]['organizations']['root']['name'])
        self.assertEqual(
            seeds[3]['organizations']['root']['name'],
            'AERES Hogeschool; HAS Hogeschool; Van Hall Larenstein'
        )
        self.assertEqual(seeds[5]['organizations']['root']['name'], 'SURFnet')

    def test_publishers_property(self):
        seeds = self.seeds
        self.assertEqual(seeds[3]['publishers'], ['AERES Hogeschool; HAS Hogeschool; Van Hall Larenstein'])
        self.assertEqual(seeds[5]['publishers'], ['SURFnet'])
        self.assertEqual(seeds[15]['publishers'], ['Erasmus Medisch Centrum'])

    def test_consortium_property(self):
        seeds = self.seeds
        self.assertEqual(seeds[3]['consortium'], None)
        self.assertEqual(seeds[15]['consortium'], 'HBO Verpleegkunde')

    def test_is_restricted(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]['is_restricted'], True, "Expected deleted material to indicate restriction")
        self.assertEqual(seeds[1]['is_restricted'], False, "Expected standard material to have no restriction")
        self.assertEqual(seeds[15]['is_restricted'], True, "Expected restricted material to indicate restriction")

    def test_analysis_allowed_property(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]['analysis_allowed'], False, "Expected deleted material to disallow analysis")
        self.assertEqual(seeds[1]['analysis_allowed'], True, "Expected standard material to allow analysis")
        self.assertEqual(
            seeds[14]['analysis_allowed'], True,
            "Expected (open) nd copyright material to allow analysis"
        )
        self.assertEqual(
            seeds[15]['analysis_allowed'], False,
            "Expected (restricted) nd copyright material to disallow analysis"
        )

    def test_ideas_property(self):
        seeds = self.seeds
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
        seeds = self.seeds
        self.assertEqual(seeds[0]["lom_educational_levels"], [],
                         "Expected deleted materials to have no educational level")
        self.assertEqual(sorted(seeds[1]["lom_educational_levels"]), ["HBO", "HBO - Bachelor"],
                         "Expected HBO materials to have an educational level")
        self.assertEqual(sorted(seeds[2]["lom_educational_levels"]), ["WO", "WO - Bachelor"],
                         "Expected HBO materials to have an educational level")

    def test_lowest_educational_level(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["lowest_educational_level"], -1,
                         "Expected deleted materials to have negative educational level")
        self.assertEqual(seeds[1]["lowest_educational_level"], 2,
                         "Expected HBO materials to have an educational level of 2")
        self.assertEqual(seeds[2]["lowest_educational_level"], 3,
                         "Expected HBO materials to have an educational level of 3")

    def test_get_files(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["files"], [], "Expected deleted material to have no files")
        self.assertEqual(len(seeds[1]["files"]), 1)

        self.assertEqual(seeds[1]["files"], [
            {
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "url": "https://surfsharekit.nl/objectstore/182216be-31a2-43c3-b7de-e5dd355b09f7",
                "hash": "0ed38cdc914e5e8a6aa1248438a1e2032a14b0de",
                "title": "URL 1",
                "access_rights": "OpenAccess",
                "copyright": "cc-by-nc-40"
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
        seeds = self.seeds
        self.assertEqual(len(seeds), 17, "Expected get_harvest_seeds to filter differently based on copyright")
        self.assertEqual(seeds[1]["copyright"], "cc-by-nc-40",
                         "Expected 'yes' copyright to look at copyright_description")
        self.assertEqual(seeds[2]["copyright"], "cc-by-40",
                         "Expected copyright to be present even though copyright_description is missing")

    def test_get_technical_type(self):
        seeds = self.seeds
        self.assertIsNone(seeds[0]["technical_type"], "Expected deleted material to have unknown technical type")
        self.assertEqual(seeds[1]["technical_type"], "document",
                         "Expected technical type to be deferred from mime type")
        self.assertEqual(seeds[2]["technical_type"], "unknown",
                         "Expected unknown technical type when mime type is unknown")

    def test_get_material_types(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["material_types"], [],
                         "Expected deleted material to have no material types")
        self.assertEqual(seeds[1]["material_types"], [],
                         "Expected material without a type to return empty list")
        self.assertEqual(seeds[4]["material_types"], ["weblecture"])

    def test_get_publisher_year(self):
        seeds = self.seeds
        self.assertIsNone(seeds[0]["publisher_year"], "Expected deleted material to have no publication year")
        self.assertIsNone(seeds[1]["publisher_year"],
                          "Expected material without publication date to have no publication year")
        self.assertEqual(seeds[3]["publisher_year"], 2017)
        self.assertEqual(seeds[8]["publisher_year"], 2020)
