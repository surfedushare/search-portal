from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from harvester.utils.extraction import get_harvest_seeds
from core.constants import Repositories
from sources.factories.hanze.extraction import HanzeResearchObjectResourceFactory, SET_SPECIFICATION


class TestGetHarvestSeedsHanze(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.begin_of_time = make_aware(datetime(year=1970, month=1, day=1))
        HanzeResearchObjectResourceFactory.create_common_responses()
        cls.seeds = get_harvest_seeds(Repositories.HANZE, SET_SPECIFICATION, cls.begin_of_time, include_no_url=True)

    def test_get_record_state(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["state"], "active")

    def test_get_id(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["external_id"], "01ea0ee1-a419-42ee-878b-439b44562098")

    def test_get_files(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["files"], [
            {
                "mime_type": "application/pdf",
                "url": "https://research-test.hanze.nl/ws/api/research-outputs/01ea0ee1-a419-42ee-878b-439b44562098/"
                       "files/NWU1MWM2/wtnr2_verh1_p99_113_HR_v2_Inter_nationale_ervaringen"
                       "_met_ondergrondse_infiltratievoorzieningen_20_jaar.pdf",
                "hash": "b20e35dd499a92d02a435be018a267a0d9d3eb89",
                "title": "wtnr2_verh1_p99_113_HR_v2_Inter_nationale_ervaringen"
                         "_met_ondergrondse_infiltratievoorzieningen_20_jaar.pdf",
                "copyright": None,
                "access_rights": "OpenAccess"
            }
        ])
        self.assertEqual(seeds[12]["files"], [
            {
                "title": "Power_to_the_people_accepted_version_1.pdf",
                "url": "https://research-test.hanze.nl/ws/api/research-outputs/3786d62c-11fa-445b-a299-cc79ea00d468/"
                       "files/MDAxYTdkM2M2/Power_to_the_people_accepted_version_1.pdf",
                "mime_type": "application/pdf",
                "hash": "8a83314d543513cdcb43329ecd78145ff45134d3",
                "copyright": None,
                "access_rights": "OpenAccess"
            }
        ])

    def test_get_url(self):
        seeds = self.seeds
        self.assertEqual(
            seeds[0]["url"],
            "https://research-test.hanze.nl/ws/api/research-outputs/01ea0ee1-a419-42ee-878b-439b44562098/"
            "files/NWU1MWM2/wtnr2_verh1_p99_113_HR_v2_Inter_nationale_ervaringen"
            "_met_ondergrondse_infiltratievoorzieningen_20_jaar.pdf"
        )

    def test_get_mime_type(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["mime_type"], "application/pdf")

    def test_get_analysis_allowed(self):
        seeds = self.seeds
        self.assertTrue(seeds[0]["analysis_allowed"], "Expected OpenAccess file to allow analysis")
        self.assertFalse(
            seeds[2]["analysis_allowed"],
            "Expected RestrictedAccess file to disallow analysis, because copyright will be unknown"
        )
        self.assertFalse(seeds[3]["analysis_allowed"], "Expected ClosedAccess file to disallow analysis")

    def test_get_language(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["language"], {"metadata": "nl"})
        self.assertEqual(seeds[1]["language"], {"metadata": "en"})

    def test_get_title(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["title"], "(Inter)nationale ervaringen met ondergrondse infiltratievoorzieningen")

    def test_get_description(self):
        seeds = self.seeds
        self.assertTrue(seeds[0]["description"].startswith("Infiltratie van afstromend regenwater is"))

    def test_keywords(self):
        seeds = self.seeds
        self.assertEqual(sorted(seeds[0]["keywords"]), [
            'Engineering(all)', 'Entrepreneurship', 'afvoer', 'infiltratie', 'ondergrond', 'regenwater',
            'stedelijke gebieden'
        ])
        self.assertEqual(sorted(seeds[1]["keywords"]), [
            '3d', 'Civil and Structural Engineering', 'disasters', 'flooding', 'overstromingen', 'rampen', 'resilience',
            'risk management', 'speerpunt energie', 'water'
        ])
        self.assertEqual(sorted(seeds[7]["keywords"]), [
            'Geography, Planning and Development', 'Liveability', 'demografische ontwikkeling', 'demography',
            'krimpgebieden', 'leefbaarheid', 'leefomgeving ', 'noord-nederland', 'northern netherlands'
        ])
        self.assertEqual(sorted(seeds[10]["keywords"]), [
            'Education', 'Honours', 'blended learning', 'community building', 'corona', 'covid-19',
            'gemeenschapsvorming', 'honours education'
        ])

    def test_authors_property(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]['authors'], [
            {
                'name': 'Woogie Boogie',
                'email': None,
                'external_id': 'f515d64c-ae09-487f-b32d-a57a66cbecd5',
                'dai': None,
                'orcid': None,
                'isni': None
            },
            {
                'name': 'Teefje Wentel',
                'email': None,
                'external_id': 'e5c04d5d-0f00-4586-9f89-42ccc81f850f',
                'dai': None,
                'orcid': None,
                'isni': None
            }
        ])

    def test_publisher_date(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["publisher_date"], "2011-11-01")
        self.assertEqual(seeds[9]["publisher_date"], "2021-02-01")

    def test_publisher_year(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["publisher_year"], 2011)
        self.assertEqual(seeds[9]["publisher_year"], 2021)

    def test_research_object_type(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["research_object_type"], "Article")

    def test_doi(self):
        seeds = self.seeds
        self.assertIsNone(seeds[0]["doi"])
        self.assertEqual(seeds[12]["doi"], "10.1016/j.rser.2014.10.089")

    def test_research_theme(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["research_themes"], ["techniek"])
        self.assertEqual(seeds[14]["research_themes"], ["economie_management", "ruimtelijkeordening_planning"])
