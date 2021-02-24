"""
Checking whether progress information from push_es_index command matches expectations.
This is a very basic high-over way to check if the command succeeds.
Alternatively the involved models can get unit tested and we can see whether command uses the right methods.
After checking basic command flow we're checking, whether the Elastic Search library was called correctly
to update the indices.
"""

from unittest.mock import patch

from django.utils.timezone import make_aware, datetime
from django.test import TestCase
from django.core.management import call_command

from core.models import Dataset, OAIPMHHarvest, ElasticIndex, Arrangement
from core.tests.mocks import get_elastic_client_mock


class ElasticSearchClientTestCase(TestCase):

    elastic_client = get_elastic_client_mock()

    def setUp(self):
        super().setUp()
        self.elastic_client.indices.put_alias.reset_mock()
        self.elastic_client.indices.create.reset_mock()
        self.elastic_client.indices.delete.reset_mock()

    def assert_document_structure(self, document, is_deleted=False):
        # Deleted documents have a very limited structure
        if is_deleted:
            self.assertEqual(document["_op_type"], "delete")
            self.assertIn("_id", document)
            self.assertIn("language", document)
            return
        # Here we check if documents have all required keys including _id
        expected_keys = {
            "title", "text", "transcription", "url", "external_id", "disciplines", "lom_educational_levels",
            "educational_levels", "author", "description", "publisher_date", "copyright", "language", "title_plain",
            "text_plain", "transcription_plain", "keywords", "file_type", "mime_type", "suggest_phrase",
            "suggest_completion", "_id", "oaipmh_set", "arrangement_collection_name", "aggregation_level", "publishers",
            "authors", "has_part", "is_part_of", "preview_path", "analysis_allowed", "ideas",
        }
        self.assertEqual(set(document.keys()), expected_keys)


class TestPushToIndex(ElasticSearchClientTestCase):
    """
    This test case represents the scenario where a all harvest data gets pushed to an index for the first time
    """

    fixtures = ["datasets-history", "resources"]
    elastic_client = get_elastic_client_mock()

    @patch("core.models.search.get_es_client", return_value=elastic_client)
    @patch("core.models.search.streaming_bulk")
    @patch("core.logging.HarvestLogger.info")
    def test_edurep_surf_with_promote(self, info_logger, streaming_bulk, get_es_client):

        # Setting basic expectations used in the test
        expected_doc_count = {
            "en": 3,
            "nl": 2
        }
        expected_index_configuration = {
            "en": ElasticIndex.get_index_config("en"),
            "nl": ElasticIndex.get_index_config("nl")
        }

        # Calling command and catching output for some checks
        call_command("push_es_index", "--dataset=test", "--promote")

        # Expect command to print what actions it will undertake and since what modification date
        info_logger.assert_any_call("since:2020-02-10, recreate:False and promote:True")
        # Expect command to print how many Dutch documents it encountered
        info_logger.assert_any_call(f"nl:{expected_doc_count['nl']}")
        # Expect command to print how many English documents it encountered
        info_logger.assert_any_call(f"en:{expected_doc_count['en']}")
        # Expect command to print how many documents it encountered with unknown language
        info_logger.assert_any_call("unk:1")

        # Asserting calls to Elastic Search library
        self.assertEqual(get_es_client.call_count, 2,
                         "Expected an Elastic Search client to get created for each language")
        for args, kwargs in streaming_bulk.call_args_list:
            client, docs = args
            index_name, language, id = kwargs["index"].split("-")
            self.assertEqual(len(docs), expected_doc_count[language])
            for doc in docs:
                self.assert_document_structure(doc)

            self.assertEqual(index_name, "test")
        self.assertEqual(self.elastic_client.indices.delete.call_count, 0)
        self.assertEqual(self.elastic_client.indices.create.call_count, 2)
        for args, kwargs in self.elastic_client.indices.create.call_args_list:
            index_name, language, id = kwargs["index"].split("-")
            self.assertEqual(index_name, "test")
            self.assertEqual(kwargs["body"], expected_index_configuration[language])
        self.assertEqual(self.elastic_client.indices.put_alias.call_count, 2,
                         "Expected an Elastic Search alias creation for each language")
        for args, kwargs in self.elastic_client.indices.put_alias.call_args_list:
            index_name, language, id = kwargs["index"].split("-")
            self.assertIn(index_name, "test")
            self.assertIn(kwargs["name"], ["latest-nl", "latest-en"])

    @patch("core.models.search.get_es_client", return_value=elastic_client)
    @patch("core.models.search.streaming_bulk")
    @patch("core.logging.HarvestLogger.info")
    def test_edurep_surf_without_promote(self, info_logger, streaming_bulk, get_es_client):

        # Setting basic expectations used in the test
        expected_doc_count = {
            "en": 3,
            "nl": 2
        }
        expected_index_configuration = {
            "en": ElasticIndex.get_index_config("en"),
            "nl": ElasticIndex.get_index_config("nl")
        }

        # Calling command and catching output for some checks
        call_command("push_es_index", "--dataset=test")

        # Expect command to print what actions it will undertake and since what modification date
        info_logger.assert_any_call("since:2020-02-10, recreate:False and promote:False")
        # Expect command to print how many Dutch documents it encountered
        info_logger.assert_any_call(f"nl:{expected_doc_count['nl']}")
        # Expect command to print how many English documents it encountered
        info_logger.assert_any_call(f"en:{expected_doc_count['en']}")
        # Expect command to print how many documents it encountered with unknown language
        info_logger.assert_any_call("unk:1")

        # Asserting calls to Elastic Search library
        self.assertEqual(get_es_client.call_count, 2,
                         "Expected an Elastic Search client to get created for each language")
        for args, kwargs in streaming_bulk.call_args_list:
            client, docs = args
            index_name, language, id = kwargs["index"].split("-")
            self.assertEqual(len(docs), expected_doc_count[language])
            for doc in docs:
                self.assert_document_structure(doc)
            self.assertIn(index_name, "test")
        self.assertEqual(self.elastic_client.indices.delete.call_count, 0)
        self.assertEqual(self.elastic_client.indices.create.call_count, 2)
        for args, kwargs in self.elastic_client.indices.create.call_args_list:
            index_name, language, id = kwargs["index"].split("-")
            self.assertEqual(index_name, "test")
            self.assertEqual(kwargs["body"], expected_index_configuration[language])
        self.assertEqual(self.elastic_client.indices.put_alias.call_count, 0,
                         "Expected Elastic Search to ignore aliases")

    def test_invalid_dataset(self):
        # Testing the case where a Dataset does not exist at all
        try:
            call_command("push_es_index", "--dataset=invalid")
            self.fail("push_es_index did not raise for an invalid dataset")
        except Dataset.DoesNotExist:
            pass


class TestPushToIndexWithHistory(ElasticSearchClientTestCase):
    """
    This test case represents the scenario where indices exist.
    Under this condition the following should be possible
     * only a small part gets updated
     * deletes from previous runs
     * complete recreate of existing indices (drop + create)
    """

    fixtures = ["datasets-history", "index-history", "surf-oaipmh-2020-01-01", "resources"]
    elastic_client = get_elastic_client_mock(has_history=True)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        deleted_arrangement = Arrangement.objects.get(
            meta__reference_id="surf:oai:surfsharekit.nl:b500d389-2fda-4696-ae51-9cd0603a48af"
        )
        deleted_arrangement.delete()

    def setUp(self):
        super().setUp()
        self.elastic_client.indices.put_alias.reset_mock()
        self.elastic_client.indices.create.reset_mock()
        self.elastic_client.indices.delete.reset_mock()

    @patch("core.models.search.get_es_client", return_value=elastic_client)
    @patch("core.models.search.streaming_bulk")
    @patch("core.logging.HarvestLogger.info")
    def test_edurep_surf_deletes(self, info_logger, streaming_bulk, get_es_client):

        # Marking the Wikiwijsmaken packages as deleted to see how that propagates
        arrangement = Arrangement.objects.get(id=92378)
        arrangement.delete()  # this sets deleted_at

        # Setting basic expectations used in the test
        expected_doc_count = {
            "en": 3,
            "nl": 2
        }
        expected_deleted_ids = [
            "surf:oai:surfsharekit.nl:b500d389-2fda-4696-ae51-9cd0603a48af",
            "surf:oai:surfsharekit.nl:63903863-6c93-4bda-b850-277f3c9ec00e",
            "surf:oai:surfsharekit.nl:63903863-6c93-4bda-b850-277f3c9ec00e-page-2935729",
            "surf:oai:surfsharekit.nl:63903863-6c93-4bda-b850-277f3c9ec00e-page-2935768",
            "surf:oai:surfsharekit.nl:63903863-6c93-4bda-b850-277f3c9ec00e-page-2935734",
            "surf:oai:surfsharekit.nl:63903863-6c93-4bda-b850-277f3c9ec00e-page-3703806",
            "surf:oai:surfsharekit.nl:63903863-6c93-4bda-b850-277f3c9ec00e-page-2935733",
            "surf:oai:surfsharekit.nl:63903863-6c93-4bda-b850-277f3c9ec00e-page-colofon",
        ]

        # Calling command and catching output for some checks
        call_command("push_es_index", "--dataset=test")

        # Expect command to print what actions it will undertake and since what modification date
        info_logger.assert_any_call("since:2020-02-10, recreate:False and promote:False")
        # Expect command to print how many Dutch documents it encountered
        info_logger.assert_any_call(f"nl:{expected_doc_count['nl']}")
        # Expect command to print how many English documents it encountered
        info_logger.assert_any_call(f"en:{expected_doc_count['en']}")
        # Expect command to print how many documents it encountered with unknown language
        info_logger.assert_any_call("unk:1")

        # Asserting calls to Elastic Search library
        self.assertEqual(get_es_client.call_count, 2,
                         "Expected an Elastic Search client to get created for each language")
        deleted_count = 0
        for args, kwargs in streaming_bulk.call_args_list:
            client, docs = args
            index_name, language, id = kwargs["index"].split("-")
            self.assertEqual(len(docs), expected_doc_count[language])
            for doc in docs:
                is_deleted = doc["_id"] in expected_deleted_ids
                if is_deleted:
                    deleted_count += 1
                self.assert_document_structure(doc, is_deleted=is_deleted)
            self.assertEqual(index_name, "test")
        self.assertEqual(deleted_count, 2)
        self.assertEqual(self.elastic_client.indices.delete.call_count, 0)
        self.assertEqual(self.elastic_client.indices.create.call_count, 0)
        self.assertEqual(self.elastic_client.indices.put_alias.call_count, 0,
                         "Expected Elastic Search to ignore aliases")

    @patch("core.models.search.get_es_client", return_value=elastic_client)
    @patch("core.models.search.streaming_bulk")
    @patch("core.logging.HarvestLogger.info")
    def test_edurep_surf_delta(self, info_logger, streaming_bulk, get_es_client):

        # Putting latest harvest into the future to test partial update
        harvested_at = make_aware(datetime(year=2020, month=6, day=1))
        OAIPMHHarvest.objects.all().update(harvested_at=harvested_at)

        # Setting basic expectations used in the test
        expected_doc_count = {
            "en": 1,
            "nl": 1
        }

        # Calling command and catching output for some checks similar to TestPushToIndex.test_edurep_surf_with_promote
        call_command("push_es_index", "--dataset=test")

        # Expect command to print what actions it will undertake and since what modification date
        info_logger.assert_any_call("since:2020-06-01, recreate:False and promote:False")
        # Expect command to print how many Dutch documents it encountered
        info_logger.assert_any_call(f"nl:{expected_doc_count['nl']}")
        # Expect command to print how many English documents it encountered
        info_logger.assert_any_call(f"en:{expected_doc_count['en']}")
        # Expect command to print how many documents it encountered with unknown language
        info_logger.assert_any_call("unk:1")

        # Asserting calls to Elastic Search library
        self.assertEqual(get_es_client.call_count, 2,
                         "Expected an Elastic Search client to get created for each language")
        for args, kwargs in streaming_bulk.call_args_list:
            client, docs = args
            index_name, language, id = kwargs["index"].split("-")
            self.assertEqual(len(docs), expected_doc_count[language])
            for doc in docs:
                self.assert_document_structure(
                    doc, doc["_id"] == "surf:oai:surfsharekit.nl:b500d389-2fda-4696-ae51-9cd0603a48af"
                )
            self.assertEqual(index_name, "test")
        self.assertEqual(self.elastic_client.indices.delete.call_count, 0)
        self.assertEqual(self.elastic_client.indices.create.call_count, 0)
        self.assertEqual(self.elastic_client.indices.put_alias.call_count, 0,
                         "Expected Elastic Search to ignore aliases")

    @patch("core.models.search.get_es_client", return_value=elastic_client)
    @patch("core.models.search.streaming_bulk")
    @patch("core.logging.HarvestLogger.info")
    def test_edurep_surf_recreate(self, info_logger, streaming_bulk, get_es_client):

        # Setting basic expectations used in the test
        expected_doc_count = {
            "en": 3,
            "nl": 2
        }
        expected_index_configuration = {
            "en": ElasticIndex.get_index_config("en"),
            "nl": ElasticIndex.get_index_config("nl")
        }
        get_es_client.reset_mock()

        # Calling command and catching output for some checks
        call_command("push_es_index", "--dataset=test", "--recreate")

        # Expect command to print what actions it will undertake and since what modification date
        info_logger.assert_any_call("since:1970-01-01, recreate:True and promote:False")
        # Expect command to print how many Dutch documents it encountered
        info_logger.assert_any_call(f"nl:{expected_doc_count['nl']}")
        # Expect command to print how many English documents it encountered
        info_logger.assert_any_call(f"en:{expected_doc_count['en']}")
        # Expect command to print how many documents it encountered with unknown language
        info_logger.assert_any_call("unk:1")

        # Asserting calls to Elastic Search library
        self.assertEqual(get_es_client.call_count, 2,
                         "Expected an Elastic Search client to get created for each language")
        for args, kwargs in streaming_bulk.call_args_list:
            client, docs = args
            index_name, language, id = kwargs["index"].split("-")
            self.assertEqual(len(docs), expected_doc_count[language])
            for doc in docs:
                self.assert_document_structure(
                    doc, doc["_id"] == "surf:oai:surfsharekit.nl:b500d389-2fda-4696-ae51-9cd0603a48af"
                )

            self.assertIn(index_name, "test")
        self.assertEqual(self.elastic_client.indices.delete.call_count, 2)
        for args, kwargs in self.elastic_client.indices.delete.call_args_list:
            index_name, language, id = kwargs["index"].split("-")
            self.assertEqual(index_name, "test")
        self.assertEqual(self.elastic_client.indices.create.call_count, 2)
        for args, kwargs in self.elastic_client.indices.create.call_args_list:
            index_name, language, id = kwargs["index"].split("-")
            self.assertEqual(index_name, "test")
            self.assertEqual(kwargs["body"], expected_index_configuration[language],
                             "Expected index configuration to come from database if one was created in the past")
        self.assertEqual(self.elastic_client.indices.put_alias.call_count, 2,
                         "Expected an Elastic Search alias creation for each language")
        for args, kwargs in self.elastic_client.indices.put_alias.call_args_list:
            index_name, language, id = kwargs["index"].split("-")
            self.assertEqual(index_name, "test")
            self.assertIn(kwargs["name"], ["latest-nl", "latest-en"])

    @patch("core.models.search.get_es_client", return_value=elastic_client)
    @patch("core.models.search.streaming_bulk")
    @patch("core.logging.HarvestLogger.info")
    def test_edurep_surf_with_promote(self, info_logger, streaming_bulk, get_es_client):

        # Setting basic expectations used in the test
        expected_doc_count = {
            "en": 3,
            "nl": 2
        }
        expected_index_configuration = {
            "en": ElasticIndex.objects.get(language="en", dataset__name="test").configuration,
            "nl": ElasticIndex.objects.get(language="nl", dataset__name="test").configuration
        }

        # Calling command and catching output for some checks
        call_command("push_es_index", "--dataset=test", "--promote")

        # Expect command to print what actions it will undertake and since what modification date
        info_logger.assert_any_call("since:2020-02-10, recreate:False and promote:True")
        # Expect command to print how many Dutch documents it encountered
        info_logger.assert_any_call(f"nl:{expected_doc_count['nl']}")
        # Expect command to print how many English documents it encountered
        info_logger.assert_any_call(f"en:{expected_doc_count['en']}")
        # Expect command to print how many documents it encountered with unknown language
        info_logger.assert_any_call("unk:1")

        # Asserting calls to Elastic Search library
        self.assertEqual(get_es_client.call_count, 4,
                         "Expected an Elastic Search client to get created for each language")
        for args, kwargs in streaming_bulk.call_args_list:
            client, docs = args
            index_name, language, id = kwargs["index"].split("-")
            self.assertEqual(len(docs), expected_doc_count[language])
            for doc in docs:
                self.assert_document_structure(
                    doc,
                    doc["_id"] == "surf:oai:surfsharekit.nl:b500d389-2fda-4696-ae51-9cd0603a48af"
                )

            self.assertEqual(index_name, "test")
        self.assertEqual(self.elastic_client.indices.delete.call_count, 0)
        self.assertEqual(self.elastic_client.indices.create.call_count, 0)
        for args, kwargs in self.elastic_client.indices.create.call_args_list:
            index_name, language, id = kwargs["index"].split("-")
            self.assertEqual(index_name, "test")
            self.assertEqual(kwargs["body"], expected_index_configuration[language])
        self.assertEqual(self.elastic_client.indices.put_alias.call_count, 2,
                         "Expected an Elastic Search alias creation for each language")
        for args, kwargs in self.elastic_client.indices.put_alias.call_args_list:
            index_name, language, id = kwargs["index"].split("-")
            self.assertIn(index_name, "test")
            self.assertIn(kwargs["name"], ["latest-nl", "latest-en"])
