from django.test import TestCase

from edurep.extraction import EDUREP_EXTRACTION_OBJECTIVE
from sharekit.extraction import SHAREKIT_EXTRACTION_OBJECTIVE


class TestConfiguration(TestCase):

    def test_extract_objectives(self):
        sharekit_objective_keys = [
            key if not key.startswith("#") and not key.startswith("@") else key[1:]
            for key in SHAREKIT_EXTRACTION_OBJECTIVE.keys()
        ]
        edurep_objective_keys = [
            key if not key.startswith("#") and not key.startswith("@") else key[1:]
            for key in EDUREP_EXTRACTION_OBJECTIVE.keys()
        ]
        self.assertEqual(sorted(sharekit_objective_keys), sorted(edurep_objective_keys),
                         "Expected Sharekit and Edurep to extract the same data")
