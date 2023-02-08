from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from sharekit.models import SharekitMetadataHarvest
from sharekit.tests.factories import SharekitMetadataHarvestFactory


class TestExtractSeeds(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SharekitMetadataHarvestFactory.create_common_sharekit_responses()
        cls.beginning_of_time = make_aware(datetime(year=1970, month=1, day=1))

    def test_extract_seeds(self):
        """
        Most checks are done in the test_get_harvest_seeds file.
        Here we only check whether the extract_seeds manager method didn't error
        and returned some results with essential fields.
        """
        seeds = SharekitMetadataHarvest.objects.extract_seeds("edusources", self.beginning_of_time)
        self.assertTrue(len(seeds) > 0)
        seed = seeds[0]
        self.assertEqual(seed["external_id"], "5af0e26f-c4d2-4ddd-94ab-7dd0bd531751")
        self.assertEqual(seed["copyright"], "cc-by-nc-40")
