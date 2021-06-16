"""
Checking whether progress information from index_dataset_version command matches expectations.
This is a very basic high-over way to check if the command succeeds.
Alternatively the involved models can get unit tested and we can see whether command uses the right methods.
After checking basic command flow we're checking, whether the Elastic Search library was called correctly
to update the indices.
"""

from unittest.mock import patch

from django.test import TestCase, override_settings
from django.core.management import call_command

from core.models import Dataset, DatasetVersion, ElasticIndex
from core.tests.mocks import get_elastic_client_mock
from core.tests.factories import DocumentFactory


class ElasticSearchClientTestCase(TestCase):

    elastic_client = get_elastic_client_mock()

    def setUp(self):
        super().setUp()
        self.elastic_client.indices.put_alias.reset_mock()
        self.elastic_client.indices.create.reset_mock()
        self.elastic_client.indices.delete.reset_mock()

    def assert_document_structure(self, document, has_text=True):
        # Here we check if documents have all required keys including _id
        expected_keys = {
            "title", "url", "external_id", "disciplines", "lom_educational_levels", "description", "publisher_date",
            "copyright", "language", "keywords", "file_type", "mime_type", "suggest_completion", "_id",
            "harvest_source",  "aggregation_level", "publishers", "authors", "has_parts", "is_part_of", "preview_path",
            "analysis_allowed", "ideas", "copyright_description", "files",
        }
        text_keys = {
            "text", "suggest_phrase",
        }
        if has_text:
            expected_keys.update(text_keys)
        self.assertEqual(set(document.keys()), expected_keys)


class TestIndexDatasetVersion(ElasticSearchClientTestCase):
    """
    This test case represents the scenario where a all harvest data gets pushed to an index for the first time
    """

    fixtures = ["datasets-history", "resources"]
    elastic_client = get_elastic_client_mock()

    @patch("core.models.search.get_es_client", return_value=elastic_client)
    @patch("core.models.search.streaming_bulk")
    @patch("core.logging.HarvestLogger.info")
    def test_index(self, info_logger, streaming_bulk, get_es_client):

        # Setting basic expectations used in the test
        expected_doc_count = {
            "en": 2,
            "nl": 3,
            "unk": 1
        }
        expected_index_configuration = {
            "en": ElasticIndex.get_index_config("en"),
            "nl": ElasticIndex.get_index_config("nl"),
            "unk": ElasticIndex.get_index_config("unk")
        }

        # Calling command and catching output for some checks
        call_command("index_dataset_version", "--dataset=test")

        # Expect command to print how many Dutch documents it encountered
        info_logger.assert_any_call(f"nl:{expected_doc_count['nl']}")
        # Expect command to print how many English documents it encountered
        info_logger.assert_any_call(f"en:{expected_doc_count['en']}")
        # Expect command to print how many documents it encountered with unknown language
        info_logger.assert_any_call(f"unk:{expected_doc_count['unk']}")

        # Asserting calls to Elastic Search library
        self.assertEqual(get_es_client.call_count, 3,
                         "Expected an Elastic Search client to get created for each language")
        for args, kwargs in streaming_bulk.call_args_list:
            client, docs = args
            index_name, version, version_id, language = kwargs["index"].split("-")
            self.assertEqual(len(docs), expected_doc_count[language])
            for doc in docs:
                self.assert_document_structure(doc)
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
        self.assertEqual(self.elastic_client.indices.delete.call_count, 0)
        self.assertEqual(self.elastic_client.indices.create.call_count, 3)
        for args, kwargs in self.elastic_client.indices.create.call_args_list:
            index_name, version, version_id, language = kwargs["index"].split("-")
            self.assertEqual(index_name, "test")
            self.assertEqual(kwargs["body"], expected_index_configuration[language])
        self.assertEqual(self.elastic_client.indices.put_alias.call_count, 3,
                         "Expected Elastic Search to ignore aliases")
        for args, kwargs in self.elastic_client.indices.put_alias.call_args_list:
            index_name, version, version_id, language = kwargs["index"].split("-")
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
            self.assertIn(kwargs["name"], ["latest-nl", "latest-en", "latest-unk"])

    def test_invalid_dataset(self):
        # Testing the case where a Dataset does not exist at all
        try:
            call_command("index_dataset_version", "--dataset=invalid")
            self.fail("index_dataset_version did not raise for an invalid dataset")
        except Dataset.DoesNotExist:
            pass


class TestIndexDatasetVersionWithHistory(ElasticSearchClientTestCase):
    """
    This test case represents the scenario where indices exist.
    Under this condition the following should be possible
    * only a small part gets updated
    * deletes from previous runs
    * complete recreate of existing indices (drop + create)
    """

    fixtures = ["datasets-history", "index-history", "surf-oaipmh-2020-01-01", "resources"]
    elastic_client = get_elastic_client_mock(has_history=True)

    @patch("core.models.search.get_es_client", return_value=elastic_client)
    @patch("core.models.search.streaming_bulk")
    @patch("core.logging.HarvestLogger.info")
    def test_index(self, info_logger, streaming_bulk, get_es_client):

        # Setting basic expectations used in the test
        expected_doc_count = {
            "en": 2,
            "nl": 3,
            "unk": 1
        }
        expected_index_configuration = {
            "en": ElasticIndex.get_index_config("en"),
            "nl": ElasticIndex.get_index_config("nl"),
            "unk": ElasticIndex.get_index_config("unk")
        }
        get_es_client.reset_mock()

        # Calling command and catching output for some checks
        call_command("index_dataset_version", "--dataset=test")

        # Expect command to print how many Dutch documents it encountered
        info_logger.assert_any_call(f"nl:{expected_doc_count['nl']}")
        # Expect command to print how many English documents it encountered
        info_logger.assert_any_call(f"en:{expected_doc_count['en']}")
        # Expect command to print how many documents it encountered with unknown language
        info_logger.assert_any_call(f"unk:{expected_doc_count['unk']}")

        # Asserting calls to Elastic Search library
        self.assertEqual(get_es_client.call_count, 3,
                         "Expected an Elastic Search client to get created for each language")
        for args, kwargs in streaming_bulk.call_args_list:
            client, docs = args
            index_name, version, version_id, language = kwargs["index"].split("-")
            self.assertEqual(len(docs), expected_doc_count[language])
            for doc in docs:
                self.assert_document_structure(doc)
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")

        self.assertEqual(self.elastic_client.indices.delete.call_count, 3)
        for args, kwargs in self.elastic_client.indices.delete.call_args_list:
            index_name, version, version_id, language = kwargs["index"].split("-")
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
        self.assertEqual(self.elastic_client.indices.create.call_count, 3)
        for args, kwargs in self.elastic_client.indices.create.call_args_list:
            index_name, version, version_id, language = kwargs["index"].split("-")
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
            self.assertEqual(kwargs["body"], expected_index_configuration[language],
                             "Expected index configuration to come from database if one was created in the past")
        self.assertEqual(self.elastic_client.indices.put_alias.call_count, 3,
                         "Expected an Elastic Search alias creation for each language")
        for args, kwargs in self.elastic_client.indices.put_alias.call_args_list:
            index_name, version, version_id, language = kwargs["index"].split("-")
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
            self.assertIn(kwargs["name"], ["latest-nl", "latest-en", "latest-unk"])

    @patch("core.models.search.get_es_client", return_value=elastic_client)
    @patch("core.models.search.streaming_bulk")
    @override_settings(VERSION="0.0.2")
    def test_index_specific_version(self, streaming_bulk, get_es_client):
        # Setup a new version and modify the old version to a single document version
        dataset = Dataset.objects.last()
        dataset.create_new_version()
        old_version = DatasetVersion.objects.get(version="0.0.1")
        old_version.document_set.clear()
        for collection in old_version.collection_set.all():
            collection.document_set.clear()
            DocumentFactory.create(dataset_version=old_version, collection=collection)
        # Expectations
        expected_doc_count = {
            "en": 2,
            "nl": 3,
            "unk": 1
        }
        # Index normally and check that the new version still holds all documents
        call_command("index_dataset_version", "--dataset=test")
        for args, kwargs in streaming_bulk.call_args_list:
            client, docs = args
            index_name, version, version_id, language = kwargs["index"].split("-")
            self.assertEqual(len(docs), expected_doc_count[language])
            for doc in docs:
                self.assert_document_structure(doc)
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "002")
        # Index the previous version and check we only get the modified documents
        get_es_client.reset_mock()
        streaming_bulk.reset_mock()
        call_command("index_dataset_version", "--dataset=test", "--harvester-version=0.0.1")
        self.assertEqual(streaming_bulk.call_count, 1)
        args, kwargs = streaming_bulk.call_args_list[0]
        client, docs = args
        index_name, version, version_id, language = kwargs["index"].split("-")
        self.assertEqual(len(docs), 1)
        for doc in docs:
            self.assert_document_structure(doc)
        self.assertEqual(index_name, "test")
        self.assertEqual(version, "001")
        self.assertEqual(self.elastic_client.indices.delete.call_count, 1)
        self.assertEqual(self.elastic_client.indices.create.call_count, 1)
        self.assertEqual(self.elastic_client.indices.put_alias.call_count, 1,
                         "Expected an Elastic Search alias creation for each language")
        for args, kwargs in self.elastic_client.indices.put_alias.call_args_list:
            index_name, version, version_id, language = kwargs["index"].split("-")
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
            self.assertIn(kwargs["name"], ["latest-nl", "latest-en", "latest-unk"])

    @patch("core.models.search.get_es_client", return_value=elastic_client)
    @patch("core.models.search.streaming_bulk")
    @patch("core.logging.HarvestLogger.info")
    def test_index_no_promote(self, info_logger, streaming_bulk, get_es_client):

        # Setting basic expectations used in the test
        expected_doc_count = {
            "en": 2,
            "nl": 3,
            "unk": 1
        }
        expected_index_configuration = {
            "en": ElasticIndex.get_index_config("en"),
            "nl": ElasticIndex.get_index_config("nl"),
            "unk": ElasticIndex.get_index_config("unk")
        }
        get_es_client.reset_mock()

        # Calling command and catching output for some checks
        call_command("index_dataset_version", "--dataset=test", "--no-promote")

        # Expect command to print how many Dutch documents it encountered
        info_logger.assert_any_call(f"nl:{expected_doc_count['nl']}")
        # Expect command to print how many English documents it encountered
        info_logger.assert_any_call(f"en:{expected_doc_count['en']}")
        # Expect command to print how many documents it encountered with unknown language
        info_logger.assert_any_call(f"unk:{expected_doc_count['unk']}")

        # Asserting calls to Elastic Search library
        self.assertEqual(get_es_client.call_count, 3,
                         "Expected an Elastic Search client to get created for each language")
        for args, kwargs in streaming_bulk.call_args_list:
            client, docs = args
            index_name, version, version_id, language = kwargs["index"].split("-")
            self.assertEqual(len(docs), expected_doc_count[language])
            for doc in docs:
                self.assert_document_structure(doc)
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")

        self.assertEqual(self.elastic_client.indices.delete.call_count, 3)
        for args, kwargs in self.elastic_client.indices.delete.call_args_list:
            index_name, version, version_id, language = kwargs["index"].split("-")
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
        self.assertEqual(self.elastic_client.indices.create.call_count, 3)
        for args, kwargs in self.elastic_client.indices.create.call_args_list:
            index_name, version, version_id, language = kwargs["index"].split("-")
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
            self.assertEqual(kwargs["body"], expected_index_configuration[language],
                             "Expected index configuration to come from database if one was created in the past")
        self.assertEqual(self.elastic_client.indices.put_alias.call_count, 0,
                         "Expected no alias creation")
