from unittest.mock import Mock

from django.test import TestCase

from core.models import DatasetVersion


class TestDatasetVersionManager(TestCase):

    def test_reduce_version_integer(self):
        test_data = {
            "0.0.1": 1,
            "1.0.1": 1000001,
            "1.20.1": 1020001,
            "10.20.999": 10020999
        }
        for string_version, expected_integer_version in test_data.items():
            dataset_version = Mock(version=string_version)
            integer_version = DatasetVersion.objects.reduce_version_integer(dataset_version)
            self.assertEqual(
                integer_version,
                expected_integer_version,
                f"Expected string '{string_version}' to become integer '{expected_integer_version}', "
                f"but got '{integer_version}'"
            )
