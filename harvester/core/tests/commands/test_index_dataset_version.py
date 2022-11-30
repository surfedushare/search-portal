"""
Checking whether progress information from index_dataset_version command matches expectations.
This is a very basic high-over way to check if the command succeeds.
Alternatively the involved models can get unit tested and we can see whether command uses the right methods.
After checking basic command flow we're checking, whether the OpenSearch library was called correctly
to update the indices.
"""

from unittest.mock import patch
from datetime import datetime

from django.test import TestCase, override_settings
from django.core.management import call_command
from django.utils.timezone import make_aware

from core.models import Dataset, DatasetVersion, ElasticIndex, Collection, Document
from core.tests.mocks import get_search_client_mock
from core.tests.factories import DatasetFactory, create_dataset_version, DocumentFactory


class OpenSearchClientTestCase(TestCase):

    search_client = get_search_client_mock()

    def setUp(self):
        super().setUp()
        self.search_client.indices.put_alias.reset_mock()
        self.search_client.indices.create.reset_mock()
        self.search_client.indices.delete.reset_mock()

    def unpack_index_name(self, index_name):
        index_name, version, version_id, site_name, language = index_name.split("-")
        return index_name, version, language, version_id, site_name

    def assert_document_structure(self, document):
        # Here we check if documents have all required keys including _id
        expected_keys = {
            "title", "url", "external_id", "studies", "lom_educational_levels", "description", "publisher_date",
            "copyright", "language", "keywords", "mime_type", "suggest_completion", "_id",
            "harvest_source",  "aggregation_level", "publishers", "authors", "has_parts", "is_part_of", "preview_path",
            "analysis_allowed", "ideas", "copyright_description", "files", "doi", "technical_type", "material_types",
            "text", "suggest_phrase", "research_object_type", "research_themes", "parties", "video", "state",
            "extension", "learning_material_disciplines_normalized", "learning_material_disciplines", "consortium",
            "disciplines", "learning_material_themes_normalized"
        }
        has_text = document["url"] and "codarts" not in document["url"] and "youtu" not in document["url"]
        if not has_text:
            self.assertIsNone(document["text"])
            self.assertIsNone(document["suggest_phrase"])
        else:
            self.assertIsInstance(document["text"], str)
            self.assertIsInstance(document["suggest_phrase"], str)
            self.assertTrue(document["text"])
            self.assertTrue(document["suggest_phrase"])
        self.assertEqual(set(document.keys()), expected_keys, document["_id"])


class TestIndexDatasetVersion(OpenSearchClientTestCase):
    """
    This test case represents the scenario where a all harvest data gets pushed to an index for the first time
    """

    fixtures = ["datasets-history"]
    search_client = get_search_client_mock()

    @patch("core.models.search.index.get_search_client", return_value=search_client)
    @patch("core.models.search.index.streaming_bulk")
    @patch("core.logging.HarvestLogger.info")
    def test_index(self, info_logger, streaming_bulk, get_search_client):

        # Setting up the database that indicates no index exists yet
        DatasetVersion.objects.all().update(is_current=False)

        # Setting basic expectations used in the test
        expected_doc_count = {
            "en": 8,
            "nl": 2,
            "unk": 3
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

        # Asserting calls to OpenSearch library
        self.assertEqual(get_search_client.call_count, 3, "Expected a client to get created for each language")
        for args, kwargs in streaming_bulk.call_args_list:
            client, docs = args
            index_name, version, language, version_id, site = self.unpack_index_name(kwargs["index"])
            self.assertEqual(len(docs), expected_doc_count[language])
            for doc in docs:
                self.assert_document_structure(doc)
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
        self.assertEqual(self.search_client.indices.delete.call_count, 0)
        self.assertEqual(self.search_client.indices.create.call_count, 3)
        for args, kwargs in self.search_client.indices.create.call_args_list:
            index_name, version, language, version_id, site = self.unpack_index_name(kwargs["index"])
            self.assertEqual(index_name, "test")
            self.assertEqual(kwargs["body"], expected_index_configuration[language])
        self.assertEqual(self.search_client.indices.put_alias.call_count, 3, "Expected to ignore aliases")
        for args, kwargs in self.search_client.indices.put_alias.call_args_list:
            index_name, version, language, version_id, site = self.unpack_index_name(kwargs["index"])
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
            self.assertIn(
                kwargs["name"],
                ["edusources-nl", "edusources-en", "edusources-unk", "publinova-nl", "publinova-en", "publinova-unk"]
            )

        self.assertEqual(DatasetVersion.objects.filter(is_current=True).count(), 1)
        dataset_version = DatasetVersion.objects.filter(is_current=True).last()
        self.assertEqual(dataset_version.id, 1)

    def test_invalid_dataset(self):
        # Testing the case where a Dataset does not exist at all
        try:
            call_command("index_dataset_version", "--dataset=invalid")
            self.fail("index_dataset_version did not raise for an invalid dataset")
        except Dataset.DoesNotExist:
            pass
        self.assertEqual(DatasetVersion.objects.filter(is_current=True).count(), 1,
                         "No changes should have been made to existing versions")


class TestIndexDatasetVersionWithHistory(OpenSearchClientTestCase):
    """
    This test case represents the scenario where indices exist.
    Under this condition the following should be possible
    * only a small part gets updated
    * deletes from previous runs
    * complete recreate of existing indices (drop + create)
    """

    fixtures = ["datasets-history", "index-history"]
    search_client = get_search_client_mock(has_history=True)

    @patch("core.models.search.index.get_search_client", return_value=search_client)
    @patch("core.models.search.index.streaming_bulk")
    @patch("core.logging.HarvestLogger.info")
    def test_index(self, info_logger, streaming_bulk, get_search_client):

        # Setting basic expectations used in the test
        expected_doc_count = {
            "en": 8,
            "nl": 2,
            "unk": 3
        }
        expected_index_configuration = {
            "en": ElasticIndex.get_index_config("en"),
            "nl": ElasticIndex.get_index_config("nl"),
            "unk": ElasticIndex.get_index_config("unk")
        }
        get_search_client.reset_mock()

        # Calling command and catching output for some checks
        call_command("index_dataset_version", "--dataset=test")

        # Expect command to print how many Dutch documents it encountered
        info_logger.assert_any_call(f"nl:{expected_doc_count['nl']}")
        # Expect command to print how many English documents it encountered
        info_logger.assert_any_call(f"en:{expected_doc_count['en']}")
        # Expect command to print how many documents it encountered with unknown language
        info_logger.assert_any_call(f"unk:{expected_doc_count['unk']}")

        # Asserting calls to OpenSearch library
        self.assertEqual(get_search_client.call_count, 3, "Expected a client to get created for each language")
        for args, kwargs in streaming_bulk.call_args_list:
            client, docs = args
            index_name, version, language, version_id, site = self.unpack_index_name(kwargs["index"])
            self.assertEqual(len(docs), expected_doc_count[language])
            for doc in docs:
                self.assert_document_structure(doc)
                if doc["_id"] == "surfsharekit:oai:surfsharekit.nl:5af0e26f-c4d2-4ddd-94ab-7dd0bd531751":
                    self.assertEqual(doc["authors"], [{"name": "The Extension Man"}],
                                     "Expected the Extension to update authors key")
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")

        self.assertEqual(self.search_client.indices.delete.call_count, 3)
        for args, kwargs in self.search_client.indices.delete.call_args_list:
            index_name, version, language, version_id, site = self.unpack_index_name(kwargs["index"])
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
        self.assertEqual(self.search_client.indices.create.call_count, 3)
        for args, kwargs in self.search_client.indices.create.call_args_list:
            index_name, version, language, version_id, site = self.unpack_index_name(kwargs["index"])
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
            self.assertEqual(kwargs["body"], expected_index_configuration[language],
                             "Expected index configuration to come from database if one was created in the past")
        self.assertEqual(self.search_client.indices.put_alias.call_count, 3,
                         "Expected alias creation for each language")
        for args, kwargs in self.search_client.indices.put_alias.call_args_list:
            index_name, version, language, version_id, site = self.unpack_index_name(kwargs["index"])
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
            self.assertIn(
                kwargs["name"],
                ["edusources-nl", "edusources-en", "edusources-unk", "publinova-nl", "publinova-en", "publinova-unk"]
            )

        self.assertEqual(DatasetVersion.objects.filter(is_current=True).count(), 1)
        dataset_version = DatasetVersion.objects.filter(is_current=True).last()
        self.assertEqual(dataset_version.id, 1)

    @patch("core.models.search.index.get_search_client", return_value=search_client)
    @patch("core.models.search.index.streaming_bulk")
    @override_settings(VERSION="0.0.2")
    def test_index_specific_version(self, streaming_bulk, get_search_client):
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
            "en": 8,
            "nl": 2,
            "unk": 3
        }
        # Index normally and check that the new version still holds all documents
        call_command("index_dataset_version", "--dataset=test")
        for args, kwargs in streaming_bulk.call_args_list:
            client, docs = args
            index_name, version, language, version_id, site = self.unpack_index_name(kwargs["index"])
            self.assertEqual(len(docs), expected_doc_count[language])
            for doc in docs:
                self.assert_document_structure(doc)
                if doc["_id"] == "surfsharekit:oai:surfsharekit.nl:5af0e26f-c4d2-4ddd-94ab-7dd0bd531751":
                    self.assertEqual(doc["authors"], [{"name": "The Extension Man"}],
                                     "Expected the Extension to update authors key")
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "002")
        self.assertEqual(DatasetVersion.objects.filter(is_current=True).count(), 1)
        dataset_version = DatasetVersion.objects.filter(is_current=True).last()
        self.assertEqual(dataset_version.id, 3)
        # Index the previous version and check we only get the modified documents
        get_search_client.reset_mock()
        streaming_bulk.reset_mock()
        call_command("index_dataset_version", "--dataset=test", "--harvester-version=0.0.1")
        self.assertEqual(streaming_bulk.call_count, 3)
        for args, kwargs in streaming_bulk.call_args_list:
            client, docs = args
            index_name, version, language, version_id, site = self.unpack_index_name(kwargs["index"])
            if language != "en":
                self.assertEqual(len(docs), 1)
            for doc in docs:
                self.assert_document_structure(doc)
                if doc["_id"] == "surfsharekit:oai:surfsharekit.nl:5af0e26f-c4d2-4ddd-94ab-7dd0bd531751":
                    self.assertEqual(doc["authors"], [{"name": "The Extension Man"}],
                                     "Expected the Extension to update authors key")
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
        self.assertEqual(self.search_client.indices.delete.call_count, 3)
        self.assertEqual(self.search_client.indices.create.call_count, 3)
        self.assertEqual(self.search_client.indices.put_alias.call_count, 3,
                         "Expected alias creation for each language")
        for args, kwargs in self.search_client.indices.put_alias.call_args_list:
            index_name, version, language, version_id, site = self.unpack_index_name(kwargs["index"])
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
            self.assertIn(
                kwargs["name"],
                ["edusources-nl", "edusources-en", "edusources-unk", "publinova-nl", "publinova-en", "publinova-unk"]
            )
        self.assertEqual(DatasetVersion.objects.filter(is_current=True).count(), 1)
        dataset_version = DatasetVersion.objects.filter(is_current=True).last()
        self.assertEqual(dataset_version.id, 1)

    @patch("core.models.search.index.get_search_client", return_value=search_client)
    @patch("core.models.search.index.streaming_bulk")
    @patch("core.logging.HarvestLogger.info")
    @override_settings(VERSION="0.0.1")
    def test_index_no_promote(self, info_logger, streaming_bulk, get_search_client):

        # Setup a new version and modify the old version to a single document version
        dataset = Dataset.objects.last()
        dataset.create_new_version()

        # Setting basic expectations used in the test
        expected_doc_count = {
            "en": 8,
            "nl": 2,
            "unk": 3
        }
        expected_index_configuration = {
            "en": ElasticIndex.get_index_config("en"),
            "nl": ElasticIndex.get_index_config("nl"),
            "unk": ElasticIndex.get_index_config("unk")
        }
        get_search_client.reset_mock()

        # Calling command and catching output for some checks
        call_command("index_dataset_version", "--dataset=test", "--no-promote")

        # Expect command to print how many Dutch documents it encountered
        info_logger.assert_any_call(f"nl:{expected_doc_count['nl']}")
        # Expect command to print how many English documents it encountered
        info_logger.assert_any_call(f"en:{expected_doc_count['en']}")
        # Expect command to print how many documents it encountered with unknown language
        info_logger.assert_any_call(f"unk:{expected_doc_count['unk']}")

        # Asserting calls to OpenSearch library
        self.assertEqual(get_search_client.call_count, 3,
                         "Expected a client to get created for each language")
        for args, kwargs in streaming_bulk.call_args_list:
            client, docs = args
            index_name, version, language, version_id, site = self.unpack_index_name(kwargs["index"])
            self.assertEqual(len(docs), expected_doc_count[language])
            for doc in docs:
                self.assert_document_structure(doc)
                if doc["_id"] == "surfsharekit:oai:surfsharekit.nl:5af0e26f-c4d2-4ddd-94ab-7dd0bd531751":
                    self.assertEqual(doc["authors"], [{"name": "The Extension Man"}],
                                     "Expected the Extension to update authors key")
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")

        self.assertEqual(self.search_client.indices.delete.call_count, 3)
        for args, kwargs in self.search_client.indices.delete.call_args_list:
            index_name, version, language, version_id, site = self.unpack_index_name(kwargs["index"])
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
        self.assertEqual(self.search_client.indices.create.call_count, 3)
        for args, kwargs in self.search_client.indices.create.call_args_list:
            index_name, version, language, version_id, site = self.unpack_index_name(kwargs["index"])
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
            self.assertEqual(kwargs["body"], expected_index_configuration[language],
                             "Expected index configuration to come from database if one was created in the past")
        self.assertEqual(self.search_client.indices.put_alias.call_count, 0,
                         "Expected no alias creation")

        self.assertEqual(DatasetVersion.objects.filter(is_current=True).count(), 1)
        dataset_version = DatasetVersion.objects.filter(is_current=True).last()
        self.assertEqual(dataset_version.id, 1)


class TestIndexDatasetVersionFallback(OpenSearchClientTestCase):
    """
    This test case creates two dataset versions and drops Document count to below the 5% mark for non-current version.
    That should result in the new version becoming the current version,
    but the documents should come from the old version as the new version got corrupted.
    """

    search_client = get_search_client_mock(has_history=True)
    dataset = None
    docs_count = None
    new_version = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dataset = DatasetFactory(name="test")
        now = make_aware(datetime.now())
        cls.docs_count = 100
        create_dataset_version(cls.dataset, "0.0.3", now, include_current=True, copies=2, docs=cls.docs_count)
        cls.original_version = cls.dataset.versions.filter(is_current=True).last()
        cls.new_version = cls.dataset.versions.filter(is_current=False).last()
        for doc in cls.new_version.document_set.all()[:6]:
            doc.delete()

    @patch("core.models.search.index.get_search_client", return_value=search_client)
    @patch("core.models.search.index.streaming_bulk")
    @patch("core.logging.HarvestLogger.info")
    def test_index(self, info_logger, streaming_bulk, get_search_client):

        expected_doc_count = {
            "en": 0,
            "nl": 100,
            "unk": 0
        }

        call_command("index_dataset_version", "--dataset=test")

        # Check models update
        current_version = DatasetVersion.objects.get_current_version()
        self.assertEqual(current_version.id, self.new_version.id, "Expected new version to become current version")
        self.assertEqual(
            Document.objects.filter(dataset_version=None).count(), 94,
            "Expected all documents from corrupted collection to get de-linked from dataset version"
        )
        self.assertEqual(
            Document.objects.filter(dataset_version=current_version).count(), 100,
            "Expected new current version to gain previous documents"
        )
        self.assertEqual(
            Collection.objects.all().count(), 3,
            "Expected corrupted version to copy collection from previous current version, creating a new Collection"
        )

        # Asserting calls to OpenSearch library
        self.assertEqual(get_search_client.call_count, 3,
                         "Expected a client to get created for each language")
        for args, kwargs in streaming_bulk.call_args_list:
            client, docs = args
            index_name, version, language, version_id, site = self.unpack_index_name(kwargs["index"])
            self.assertEqual(int(version_id), self.new_version.id, "Expected new version to get promoted")
            self.assertEqual(len(docs), expected_doc_count[language])
            for doc in docs:
                self.assert_document_structure(doc)
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "003")

        # Check that cleanup still works correctly even if documents lost direct versions link
        deleted = current_version.delete()
        self.assertEqual(
            deleted,
            (197, {
                "core.DatasetVersion": 1,
                "core.Collection": 2,
                "core.Document": 194
            })
        )
