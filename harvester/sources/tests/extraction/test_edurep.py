from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from harvester.utils.extraction import get_harvest_seeds
from core.constants import Repositories
from sources.factories.edurep.extraction import EdurepJsonSearchResourceFactory, SET_SPECIFICATION


class TestGetHarvestSeedsEdurep(TestCase):

    begin_of_time = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.begin_of_time = make_aware(datetime(year=1970, month=1, day=1))
        EdurepJsonSearchResourceFactory.create_common_responses()
        cls.seeds = get_harvest_seeds(Repositories.EDUREP_JSONSEARCH, SET_SPECIFICATION, cls.begin_of_time)

    def test_get_id(self):
        seeds = self.seeds
        self.assertEqual(seeds[0]["external_id"], "7288bd68-d62b-4db0-8cea-5f189e209254")

