"""
Checking whether progress information from index_dataset_version command matches expectations.
This is a very basic high-over way to check if the command succeeds.
Alternatively the involved models can get unit tested and we can see whether command uses the right methods.
After checking basic command flow we're checking, whether the Elastic Search library was called correctly
to update the indices.
"""

from unittest.mock import patch

from django.test import TestCase, override_settings
from django.core.management import call_command, CommandError

from core.models import Dataset, DatasetVersion, ElasticIndex
from core.tests.mocks import get_elastic_client_mock


class TestPromoteDatasetVersion(TestCase):
    """
    This test case represents the scenario where indices exist.
    Under this condition the following should be possible
    * only a small part gets updated
    * deletes from previous runs
    * complete recreate of existing indices (drop + create)
    """

    fixtures = ["datasets-history", "index-history", "surf-oaipmh-2020-01-01", "resources"]
    elastic_client = get_elastic_client_mock(has_history=True)

    def setUp(self):
        super().setUp()
        self.elastic_client.indices.put_alias.reset_mock()
        self.elastic_client.indices.create.reset_mock()
        self.elastic_client.indices.delete.reset_mock()

    def assert_index_promoted(self):
        # Indices should not get recreated
        self.assertEqual(self.elastic_client.indices.delete.call_count, 0)
        self.assertEqual(self.elastic_client.indices.create.call_count, 0)
        # Latest alias should update
        self.assertEqual(self.elastic_client.indices.put_alias.call_count, 2)
        for args, kwargs in self.elastic_client.indices.put_alias.call_args_list:
            index_name, version, language, id = kwargs["index"].split("-")
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
            self.assertIn(kwargs["name"], ["latest-nl", "latest-en"])

    @override_settings(VERSION="0.0.1")
    @patch("core.models.search.get_es_client", return_value=elastic_client)
    def test_promote_dataset(self, get_es_client):
        get_es_client.reset_mock()
        call_command("promote_dataset_version", "--dataset=test")
        self.assert_index_promoted()

        get_es_client.reset_mock()
        call_command("promote_dataset_version", "--dataset=test", "--harvester-version=0.0.1")
        self.assert_index_promoted()

    @patch("core.models.search.get_es_client", return_value=elastic_client)
    def test_promote_dataset_version(self, get_es_client):
        get_es_client.reset_mock()
        call_command("promote_dataset_version", "--dataset-version=1")
        self.assert_index_promoted()

    def test_promote_invalid(self):
        try:
            call_command("promote_dataset_version")
            self.fail("Expected promote_dataset_version to fail with dataset and dataset_version unspecified")
        except CommandError:
            pass
        try:
            call_command("promote_dataset_version", "--dataset=test", "--harvester-version=0.0.2")
            self.fail("Expected promote_dataset_version to fail with invalid harvester version specified")
        except CommandError:
            pass
