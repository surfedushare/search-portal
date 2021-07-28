from unittest.mock import patch
from datetime import datetime

from django.test import TestCase
from django.core.management import call_command, CommandError
from django.utils.timezone import make_aware

from datagrowth.resources.http.tasks import send
from core.management.commands.harvest_metadata import Command as DatasetCommand
from core.models import DatasetVersion, Collection, Harvest
from core.constants import HarvestStages, Repositories
from core.logging import HarvestLogger
from harvester.utils.extraction import get_harvest_seeds
from edurep.tests.factories import EdurepOAIPMHFactory


GET_HARVEST_SEEDS_TARGET = "core.management.commands.harvest_metadata.get_harvest_seeds"
HANDLE_UPSERT_SEEDS_TARGET = "core.management.commands.harvest_metadata.Command.handle_upsert_seeds"
HANDLE_DELETION_SEEDS_TARGET = "core.management.commands.harvest_metadata.Command.handle_deletion_seeds"
DUMMY_SEEDS = [
    {"state": "active", "url": "https://www.vn.nl/speciaalmelk-rechtstreeks-koe/", "mime_type": "text/html"},
    {
        "state": "active",
        "url": "http://www.samhao.nl/webopac/MetaDataEditDownload.csp?file=2:145797:1",
        "mime_type": "application/pdf"
    },
    {
        "state": "active",
        "url": "https://maken.wikiwijs.nl/94812/Macro_meso_micro#!page-2935729",
        "mime_type": "text/html"
    },
    {"state": "deleted", "url": None, "mime_type": None}
]


class TestMetadataHarvest(TestCase):
    """
    This test case represents the scenario where a harvest is started from t=0
    """

    fixtures = ["datasets-new"]

    def setUp(self):
        EdurepOAIPMHFactory.create_common_edurep_responses()
        super().setUp()

    def get_command_instance(self):
        command = DatasetCommand()
        command.logger = HarvestLogger("test", "harvest_metadata", {})
        command.batch_size = 32
        return command

    @patch(GET_HARVEST_SEEDS_TARGET, return_value=DUMMY_SEEDS)
    @patch(HANDLE_UPSERT_SEEDS_TARGET, return_value=[0, 7, 14])
    @patch(HANDLE_DELETION_SEEDS_TARGET, return_value=[1, 3])
    def test_edurep_surfsharekit(self, deletion_target, upsert_target, seeds_target):
        # Checking whether end result of the command returned by "handle" matches expectations.
        # We'd expect two OAI-PMH calls to be made which should be both a success.
        # Apart from the main results we want to check if Datagrowth was used for execution.
        # This makes sure that a lot of edge cases will be covered like HTTP errors.
        with patch("core.management.commands.harvest_metadata.send", wraps=send) as send_mock:
            call_command("harvest_metadata", "--dataset=test", f"--repository={Repositories.EDUREP}")
        # Asserting Datagrowth usage
        self.assertEqual(send_mock.call_count, 1, "More than 1 call to send, was edurep_delen set not ignored?")
        args, kwargs = send_mock.call_args
        config = kwargs["config"]
        self.assertEqual(config.resource, "edurep.EdurepOAIPMH", "Wrong resource used for OAI-PMH calls")
        self.assertEqual(
            config.continuation_limit, 10000, "Expected very high continuation limit to assert complete sets"
        )
        self.assertEqual(args, ("surfsharekit", "1970-01-01"), "Wrong arguments given to edurep.EdurepOAIPMH")
        self.assertEqual(kwargs["method"], "get", "edurep.EdurepOAIPMH is not using HTTP GET method")
        # Asserting usage of get_harvest_seeds
        seeds_target.assert_called_once_with("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)),
                                             include_no_url=True)
        # Asserting usage of handle_upsert_seeds
        upsert_target.assert_called_once()
        args, kwargs = upsert_target.call_args
        self.assertIsInstance(args[0], Collection)
        self.assertEqual(args[1], DUMMY_SEEDS[:-1])
        # And then usage of handle_deletion_seeds
        deletion_target.assert_called_once()
        args, kwargs = deletion_target.call_args
        self.assertIsInstance(args[0], Collection)
        self.assertEqual(args[1], DUMMY_SEEDS[-1:])
        # Check the collection
        # Only one set was eligible for a harvest
        self.assertEqual(Collection.objects.all().count(), 1)
        collection = Collection.objects.last()
        self.assertEqual(collection.name, "surfsharekit")
        self.assertEqual(collection.dataset_version.version, "0.0.1")
        self.assertEqual(collection.referee, "external_id")
        # Last but not least we check that the correct EdurepHarvest objects have indeed progressed
        # to prevent repetitious harvests.
        surf_harvest = Harvest.objects.get(source__spec="surfsharekit")
        self.assertGreater(
            surf_harvest.harvested_at,
            make_aware(datetime(year=1970, month=1, day=1)),
            "surf set harvested_at should got updated to prevent re-harvest in the future"
        )
        edurep_delen_harvest = Harvest.objects.get(source__spec="edurep_delen")
        self.assertEqual(
            edurep_delen_harvest.latest_update_at, make_aware(datetime(year=1970, month=1, day=1)),
            "edurep_delen set harvest got updated while we expected it to be ignored"
        )

    @patch("core.management.base.PipelineCommand.logger", spec_set=HarvestLogger)
    def test_edurep_invalid_dataset(self, logger_mock):
        # Testing the case where a Dataset does not exist at all
        call_command("harvest_metadata", "--dataset=invalid", f"--repository={Repositories.EDUREP}")
        logger_mock.end.assert_called_with("seeds.edurep", fail=0, success=0)
        # Testing the case where a Dataset exists, but no harvest tasks are present
        logger_mock.end.reset_mock()
        surf_harvest = Harvest.objects.get(source__spec="surfsharekit")
        surf_harvest.stage = HarvestStages.COMPLETE
        surf_harvest.save()
        call_command("harvest_metadata", "--dataset=test", f"--repository={Repositories.EDUREP}")
        logger_mock.end.assert_called_with("seeds.edurep", fail=0, success=0)

    def test_edurep_down(self):
        with patch("core.management.commands.harvest_metadata.send", return_value=([], [100],)):
            try:
                call_command("harvest_metadata", "--dataset=test", f"--repository={Repositories.EDUREP}")
                self.fail("harvest_metadata did not fail when Resource was returning errors")
            except CommandError:
                pass

    def test_handle_upsert_seeds(self):
        dataset_version = DatasetVersion.objects.last()
        collection = Collection.objects.create(
            name="surfsharekit",
            dataset_version=dataset_version,
            referee="external_id"
        )
        command = self.get_command_instance()
        upserts = [
            seed
            for seed in get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
            if seed.get("state", "active") == "active"
        ]
        documents_count = command.handle_upsert_seeds(collection, upserts)
        # When dealing with an entirely new Dataset
        # Then the document count should equal output of handle_upsert_seeds
        self.assertEqual(collection.document_set.count(), documents_count)
        for document in collection.document_set.all():
            self.assertEqual(document.reference, document.properties["external_id"])
            metadata_pipeline = document.pipeline["metadata"]
            self.assertEqual(metadata_pipeline["resource"], "edurep.edurepoaipmh")
            self.assertIsInstance(metadata_pipeline["id"], int)
            self.assertTrue(metadata_pipeline["success"])

    def test_handle_deletion_seeds(self):
        dataset_version = DatasetVersion.objects.last()
        collection = Collection.objects.create(name="surfsharekit", dataset_version=dataset_version)
        command = self.get_command_instance()
        deletes = [
            seed
            for seed in get_harvest_seeds("surfsharekit", make_aware(datetime(year=1970, month=1, day=1)))
            if seed.get("state", "active") != "active"
        ]
        # Basically we're testing that deletion seeds are not triggering errors when their targets do not exist.
        command.handle_deletion_seeds(collection, deletes)
        self.assertEqual(collection.document_set.count(), 0)


class TestMetadataHarvestWithHistory(TestCase):
    """
    This test case represents the scenario where a harvest from a previous harvest
    """

    fixtures = ["datasets-history"]

    def setUp(self):
        EdurepOAIPMHFactory.create_common_edurep_responses(include_delta=True)
        super().setUp()

    def get_command_instance(self):
        command = DatasetCommand()
        command.logger = HarvestLogger("test", "harvest_metadata", {})
        command.batch_size = 32
        return command

    @patch(GET_HARVEST_SEEDS_TARGET, return_value=DUMMY_SEEDS)
    @patch(HANDLE_UPSERT_SEEDS_TARGET, return_value=[0, 7, 14])
    @patch(HANDLE_DELETION_SEEDS_TARGET, return_value=[1, 3])
    def test_edurep_surfsharekit(self, deletion_target, upsert_target, seeds_target):
        # Checking whether end result of the command returned by "handle" matches expectations.
        # We'd expect one OAI-PMH calls to be made which should be a success.
        # Apart from the main results we want to check if Datagrowth was used for execution.
        # This makes sure that a lot of edge cases will be covered like HTTP errors.
        test_harvest = Harvest.objects.get(source__spec="surfsharekit")
        test_harvest.prepare()
        with patch("core.management.commands.harvest_metadata.send", wraps=send) as send_mock:
            call_command("harvest_metadata", "--dataset=test", f"--repository={Repositories.EDUREP}")
        # Asserting Datagrowth usage
        self.assertEqual(send_mock.call_count, 1, "More than 1 call to send, was edurep_delen set not ignored?")
        args, kwargs = send_mock.call_args
        config = kwargs["config"]
        self.assertEqual(config.resource, "edurep.EdurepOAIPMH", "Wrong resource used for OAI-PMH calls")
        self.assertEqual(
            config.continuation_limit, 10000, "Expected very high continuation limit to assert complete sets"
        )
        self.assertEqual(args, ("surfsharekit", "2020-02-10"), "Wrong arguments given to edurep.EdurepOAIPMH")
        self.assertEqual(kwargs["method"], "get", "edurep.EdurepOAIPMH is not using HTTP GET method")
        # Asserting usage of get_harvest_seeds
        expected_since = make_aware(
            datetime(year=2020, month=2, day=10, hour=13, minute=8, second=39, microsecond=315000)
        )
        seeds_target.assert_called_once_with("surfsharekit", expected_since, include_no_url=True)
        # Asserting usage of handle_upsert_seeds
        upsert_target.assert_called_once()
        args, kwargs = upsert_target.call_args
        self.assertIsInstance(args[0], Collection)
        self.assertEqual(args[1], DUMMY_SEEDS[:-1])
        # And then usage of handle_deletion_seeds
        deletion_target.assert_called_once()
        args, kwargs = deletion_target.call_args
        self.assertIsInstance(args[0], Collection)
        self.assertEqual(args[1], DUMMY_SEEDS[-1:])
        # Last but not least we check that the correct EdurepHarvest objects have indeed progressed
        # to prevent repetitious harvests.
        surf_harvest = Harvest.objects.get(source__spec="surfsharekit")
        self.assertGreater(
            surf_harvest.harvested_at,
            make_aware(datetime(year=2020, month=2, day=10)),
            "surf set harvested_at should got updated to prevent re-harvest in the future"
        )
        edurep_delen_harvest = Harvest.objects.get(source__spec="edurep_delen")
        self.assertEqual(
            edurep_delen_harvest.latest_update_at, make_aware(datetime(year=1970, month=1, day=1)),
            "edurep_delen set harvest got updated while we expected it to be ignored"
        )

    def test_handle_upsert_seeds(self):
        dataset_version = DatasetVersion.objects.last()
        collection = Collection.objects.get(name="surfsharekit", dataset_version=dataset_version, referee="external_id")
        command = self.get_command_instance()
        # Checking the state before the test
        document_count = collection.document_set.count()
        vortex_queryset = collection.documents.filter(properties__title="Using a Vortex | Wageningen UR")
        self.assertEqual(vortex_queryset.count(), 1,
                         "Expected the start state to contain 'Using a Vortex'")
        for doc in collection.documents.all():
            self.assertEqual(doc.created_at, doc.modified_at, f"Document is unexpectedly updated: {doc.id}")
        # Perform the test
        upserts = [
            seed
            for seed in get_harvest_seeds("surfsharekit", make_aware(datetime(year=2019, month=12, day=31)))
            if seed.get("state", "active") == "active"
        ]
        command.handle_upsert_seeds(collection, upserts)
        # Checking the state after the test
        self.assertEqual(collection.document_set.count(), document_count+3)
        # Check video documents content updates
        vortex_updateset = collection.documents.filter(properties__title="Using a Vortex (responsibly) | Wageningen UR")
        self.assertEqual(vortex_updateset.count(), 1)
        self.assertEqual(vortex_queryset.count(), 0)
        # Check regular document content updates
        handson_insertset = collection.documents.filter(
            properties__title="Hands-off exercise based on WEKA - Tuning and Testing"
        )
        self.assertEqual(handson_insertset.count(), 1)
        processed_ids = set()
        for update in vortex_updateset:
            self.assertNotEqual(update.created_at, update.modified_at,
                                f"Document is unexpectedly not updated: {update.id}")
            self.assertEqual(update.reference, update.properties["external_id"])
            processed_ids.add(update.id)
        for insert in handson_insertset:
            self.assertEqual(insert.created_at.replace(microsecond=0), insert.modified_at.replace(microsecond=0),
                             f"Document is unexpectedly not inserted: {insert.id}")
            self.assertEqual(insert.reference, insert.properties["external_id"])
            processed_ids.add(insert.id)
        not_updated = collection.documents.exclude(id__in=processed_ids)
        self.assertNotEqual(not_updated.count(), 0)
        for not_update in not_updated:
            self.assertEqual(
                not_update.created_at.replace(microsecond=0), not_update.modified_at.replace(microsecond=0),
                f"Document is unexpectedly updated after upsert: {not_update.id}"
            )

    def test_handle_deletion_seeds(self):
        dataset_version = DatasetVersion.objects.last()
        collection = Collection.objects.get(name="surfsharekit", dataset_version=dataset_version)
        command = self.get_command_instance()
        document_count = collection.document_set.count()
        deletes = [
            seed
            for seed in get_harvest_seeds("surfsharekit", make_aware(datetime(year=2019, month=12, day=31)))
            if seed.get("state", "active") != "active"
        ]
        document_deletes = command.handle_deletion_seeds(collection, deletes)
        self.assertEqual(document_deletes, 1)
        self.assertEqual(collection.document_set.count(), document_count - document_deletes)
