from unittest.mock import patch
from io import StringIO

from django.test import TestCase
from django.core.management import call_command

from core.models import Dataset
from core.tests.mocks import get_elastic_client_mock


class TestPushToIndex(TestCase):
    """
    This test case represents the scenario where a all harvest data gets pushed to an index for the first time
    """

    fixtures = ["datasets-history"]
    elastic_client = get_elastic_client_mock()

    def assert_document_structure(self, document):
        expected_keys = {"title", "text", "transcription", "url", "external_id", "disciplines",
                             "educational_levels", "author", "description", "publisher_date", "copyright", "language",
                             "title_plain", "text_plain", "transcription_plain", "keywords", "file_type", "mime_type",
                             "suggest", "_id", "oaipmh_set", "arrangement_collection_name"}
        self.assertEqual(set(document.keys()), expected_keys)

    @patch("core.models.search.get_es_client", return_value=elastic_client)
    @patch("core.models.search.streaming_bulk")
    def test_edurep_surf(self, streaming_bulk, get_es_client):
        # Checking whether progress information from command matches expectations.
        # This is a very basic high-over way to check if the command succeeds.
        # Alternatively the involved models can get unit tested and we can see whether command uses the right methods.
        # After checking basic command flow we're checking,
        # whether the Elastic Search library was called correctly to update the indices.
        out = StringIO()
        call_command("push_es_index", "--dataset=test", "--no-progress", "--promote", stdout=out)
        # Asserting output
        stdout = out.getvalue().split("\n")
        results = [rsl for rsl in stdout if rsl]
        self.assertIn(
            "since:2020-02-10, recreate:False and promote:True",
            results,
            "Expected command to print what actions it will undertake and since what modification date"
        )
        self.assertIn("nl:2", results,
                      "Expected command to print how many Dutch documents it encountered")
        self.assertIn("en:3", results,
                      "Expected command to print how many English documents it encountered")
        self.assertIn("unk:1", results,
                      "Expected command to print how many documents it encountered with unknown language")
        # Asserting calls to Elastic Search library
        self.assertEqual(get_es_client.call_count, 2,
                         "Expected an Elastic Search client to get created for each language")
        for args, kwargs in streaming_bulk.call_args.call_list():
           client, docs = args
           for doc in docs:
               self.assert_document_structure(doc)
           self.assertIn(kwargs["index"], ["delta-nl-1", "delta-en-2"])
        # print(self.elastic_client.indices.put_alias.call_count)

    def test_invalid_dataset(self):
        # Testing the case where a Dataset does not exist at all
        try:
            call_command("push_es_index", "--dataset=invalid")
            self.fail("push_es_index did not raise for an invalid dataset")
        except Dataset.DoesNotExist:
            pass


# class TestPushToIndexWithHistory(TestCase):
#     """
#     This test case represents the scenario where a harvest from a previous harvest
#     """
#
#     fixtures = ["datasets-history", "surf-oaipmh-2020-01-01", "datasets-history-pre-delete"]
#
#     def test_edurep_surf(self):
#         # Checking whether end result of the command returned by "handle" matches expectations.
#         # We'd expect one OAI-PMH calls to be made which should be a success.
#         # Apart from the main results we want to check if Datagrowth was used for execution.
#         # This makes sure that a lot of edge cases will be covered like HTTP errors.
#         out = StringIO()
#         with patch("edurep.management.commands.harvest_edurep_seeds.send", wraps=send) as send_mock:
#             call_command("harvest_edurep_seeds", "--dataset=delta", "--no-progress", stdout=out)
#         # Asserting main result (ignoring any white lines at the end of output)
#         stdout = out.getvalue().split("\n")
#         stdout.reverse()
#         result = next((rsl for rsl in stdout if rsl))
#         self.assertEqual(result, "OAI-PMH: 1/1")
#         # Asserting Datagrowth usage
#         self.assertEqual(send_mock.call_count, 1, "More than 1 call to send, was edurep_delen set not ignored?")
#         args, kwargs = send_mock.call_args
#         config = kwargs["config"]
#         self.assertEqual(config.resource, "edurep.EdurepOAIPMH", "Wrong resource used for OAI-PMH calls")
#         self.assertEqual(
#             config.continuation_limit, 1000, "Expected very high continuation limit to assert complete sets"
#         )
#         self.assertEqual(args, ("surf", "2020-02-10"), "Wrong arguments given to edurep.EdurepOAIPMH")
#         self.assertEqual(kwargs["method"], "get", "edurep.EdurepOAIPMH is not using HTTP GET method")
#         # Last but not least we check that the correct EdurepHarvest objects have indeed progressed
#         # to prevent repetitious harvests.
#         surf_harvest = OAIPMHHarvest.objects.get(source__spec="surf")
#         self.assertGreater(
#             surf_harvest.harvested_at,
#             make_aware(datetime(year=2020, month=2, day=10)),
#             "surf set harvested_at should got updated to prevent re-harvest in the future"
#         )
#         edurep_delen_harvest = OAIPMHHarvest.objects.get(source__spec="edurep_delen")
#         self.assertEqual(
#             edurep_delen_harvest.latest_update_at, make_aware(datetime(year=1970, month=1, day=1)),
#             "edurep_delen set harvest got updated while we expected it to be ignored"
#         )
#         # Check if Arrangement and documents got removed correctly
#         try:
#             Arrangement.objects.get(id=73743)
#             self.fail("Old deleted Arrangement did not get removed")
#         except Arrangement.DoesNotExist:
#             pass
#         try:
#             Document.objects.get(id=197515)
#             self.fail("Old deleted Document did not get removed")
#         except Document.DoesNotExist:
#             pass
