from unittest.mock import patch
from datetime import datetime

from django.test import TestCase
from django.core.management import call_command
from django.utils.timezone import make_aware

from core.models import DatasetVersion, Collection, Harvest
from core.constants import HarvestStages
from core.management.commands.update_dataset import Command as DatasetCommand
from core.logging import HarvestLogger
from harvester.utils.extraction import get_harvest_seeds


GET_HARVEST_SEEDS_TARGET = "core.management.commands.update_dataset.get_harvest_seeds"
HANDLE_UPSERT_SEEDS_TARGET = "core.management.commands.update_dataset.Command.handle_upsert_seeds"
HANDLE_DELETION_SEEDS_TARGET = "core.management.commands.update_dataset.Command.handle_deletion_seeds"
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


class TestCreateOrUpdateDatasetNoHistory(TestCase):

    fixtures = ["datasets-new", "surf-oaipmh-1970-01-01", "resources"]

    def setUp(self):
        # Moving the VIDEO source to complete to test it gets ignored by the dataset command
        # Setting the stage of the "surf" set harvests to VIDEO
        # The only valid stage for "update_dataset" to act on.
        Harvest.objects.filter(stage=HarvestStages.VIDEO).update(stage=HarvestStages.COMPLETE)
        Harvest.objects.filter(source__spec="surf").update(stage=HarvestStages.VIDEO)
        super().setUp()

    def get_command_instance(self):
        command = DatasetCommand()
        command.logger = HarvestLogger("test", "update_dataset", {})
        command.batch_size = 32
        return command

    @patch(GET_HARVEST_SEEDS_TARGET, return_value=DUMMY_SEEDS)
    @patch(HANDLE_UPSERT_SEEDS_TARGET, return_value=[0, 7, 14])
    @patch(HANDLE_DELETION_SEEDS_TARGET, return_value=[1, 3])
    def test_dataset(self, deletion_target, upsert_target, seeds_target):
        # Checking whether end result of the command returned by "handle" matches expectations.
        # We'd expect the command to get seeds from get_harvest_seeds function.
        # After that the modifications to the dataset are done by two methods named:
        # handle_upsert_seeds and handle_deletion_seeds.
        # We'll test those separately, but check if they get called with the seeds returned by get_harvest_seeds
        call_command("update_dataset", "--dataset=test")
        # Asserting usage of get_harvest_seeds
        seeds_target.assert_called_once_with("surf", make_aware(datetime(year=1970, month=1, day=1)),
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
        # Last but not least we check that the correct EdurepHarvest objects have indeed progressed
        # to prevent repetitious harvests.
        surf_harvest = Harvest.objects.get(source__spec="surf")
        self.assertEqual(
            surf_harvest.stage,
            HarvestStages.PREVIEW,
            "surf set harvest should got updated to stage BASIC to prevent re-harvest in the future"
        )
        edurep_delen_harvest = Harvest.objects.get(source__spec="edurep_delen")
        self.assertEqual(
            edurep_delen_harvest.stage,
            HarvestStages.COMPLETE,
            "edurep_delen set harvest got updated to other than COMPLETE while we expected it to be ignored"
        )

    def test_basic_invalid_dataset(self):
        # Testing the case where a Dataset does not exist at all
        try:
            call_command("update_dataset", "--dataset=invalid")
            self.fail("update_dataset did not raise for an invalid dataset")
        except Harvest.DoesNotExist:
            pass
        # Testing the case where a Dataset exists, but no harvest tasks are present
        surf_harvest = Harvest.objects.get(source__spec="surf")
        surf_harvest.stage = HarvestStages.BASIC
        surf_harvest.save()
        try:
            call_command("update_dataset", "--dataset=test")
            self.fail("update_dataset did not raise for a dataset without pending harvests")
        except Harvest.DoesNotExist:
            pass

    def test_handle_upsert_seeds(self):
        dataset_version = DatasetVersion.objects.last()
        collection = Collection.objects.create(name="surf", dataset_version=dataset_version)
        command = self.get_command_instance()
        upserts = [
            seed
            for seed in get_harvest_seeds("surf", make_aware(datetime(year=1970, month=1, day=1)))
            if seed.get("state", "active") == "active"
        ]
        skipped, documents_count = command.handle_upsert_seeds(collection, upserts)
        # When dealing with an entirely new Dataset
        # Then the document count should equal output of handle_upsert_seeds
        self.assertEqual(collection.document_set.count(), documents_count)
        # Check that we allow passing through of documents that were unable to fetch content
        text_count = 0
        for doc in collection.document_set.all():
            if doc.properties.get("text", None):
                text_count += 1
        self.assertGreater(text_count, 0, "No documents with texts found")
        self.assertGreater(documents_count - text_count, 0, "No documents without texts found")
        # Check that pipelines are filled correctly
        for doc in collection.document_set.all():
            for phase, result in doc.properties["pipeline"].items():
                if phase == "harvest":
                    self.assertIsInstance(result, str)
                else:
                    self.assertIn("success", result)
                    self.assertIn("resource", result)

    def test_handle_deletion_seeds(self):
        dataset_version = DatasetVersion.objects.last()
        collection = Collection.objects.create(name="surf", dataset_version=dataset_version)
        command = self.get_command_instance()
        deletes = [
            seed
            for seed in get_harvest_seeds("surf", make_aware(datetime(year=1970, month=1, day=1)))
            if seed.get("state", "active") != "active"
        ]
        # Basically we're testing that deletion seeds are not triggering errors when their targets do not exist.
        command.handle_deletion_seeds(collection, deletes)
        self.assertEqual(collection.document_set.count(), 0)


class TestCreateOrUpdateDatasetWithHistory(TestCase):

    fixtures = ["datasets-history", "surf-oaipmh-2020-01-01", "resources"]

    def setUp(self):
        # Setting the stage of the "surf" set harvests to VIDEO.
        # The only valid stage for "update_dataset" to act on.
        Harvest.objects.filter(source__spec="surf").update(stage=HarvestStages.VIDEO)
        super().setUp()

    def get_command_instance(self):
        command = DatasetCommand()
        command.logger = HarvestLogger("test", "update_dataset", {})
        command.batch_size = 32
        return command

    def test_handle_upsert_seeds(self):
        dataset_version = DatasetVersion.objects.last()
        collection = Collection.objects.get(name="surf", dataset_version=dataset_version)
        command = self.get_command_instance()
        # Checking the state before the test
        document_count = collection.document_set.count()
        vortex_queryset = collection.documents.filter(properties__title="Using a Vortex | Wageningen UR")
        handson_queryset = collection.documents.filter(
            properties__title="Hands-on exercise based on WEKA - Tuning and Testing"
        )
        self.assertEqual(vortex_queryset.count(), 1,
                         "Expected the start state to contain 'Using a Vortex'")
        self.assertEqual(handson_queryset.count(), 1, "Expected the start state to contain 'Hands-on exercise'")
        for doc in collection.documents.all():
            self.assertEqual(doc.created_at, doc.modified_at, f"Document is unexpectedly updated: {doc.id}")
        # Perform the test
        upserts = [
            seed
            for seed in get_harvest_seeds("surf", make_aware(datetime(year=2019, month=12, day=31)))
            if seed.get("state", "active") == "active"
        ]
        skipped, documents_count = command.handle_upsert_seeds(collection, upserts)
        # Checking the state after the test
        self.assertEqual(skipped, 0)
        self.assertEqual(collection.document_set.count(), document_count+2)
        # Check video documents content updates
        vortex_updateset = collection.documents.filter(properties__title="Using a Vortex (responsibly) | Wageningen UR")
        self.assertEqual(vortex_updateset.count(), 1)
        self.assertEqual(vortex_queryset.count(), 0)
        # Check regular document content updates
        handson_updateset = collection.documents.filter(
            properties__title="Hands-off exercise based on WEKA - Tuning and Testing"
        )
        self.assertEqual(handson_updateset.count(), 1)
        self.assertEqual(handson_queryset.count(), 0)
        update_ids = set()
        for update in vortex_updateset:
            self.assertNotEqual(update.created_at, update.modified_at,
                                f"Document is unexpectedly not updated: {update.id}")
            update_ids.add(update.id)
        for update in handson_updateset:
            self.assertNotEqual(update.created_at, update.modified_at,
                                f"Document is unexpectedly not updated: {update.id}")
            update_ids.add(update.id)
        not_updated = collection.documents.exclude(id__in=update_ids)
        self.assertNotEqual(not_updated.count(), 0)
        for not_update in not_updated:
            self.assertEqual(
                not_update.created_at.replace(microsecond=0), not_update.modified_at.replace(microsecond=0),
                f"Document is unexpectedly updated after upsert: {not_update.id}"
            )
        # Check that pipelines are filled correctly
        for doc in collection.document_set.all():
            for phase, result in doc.properties["pipeline"].items():
                if phase == "harvest":
                    self.assertIsInstance(result, str)
                else:
                    self.assertIn("success", result)
                    self.assertIn("resource", result)

    def test_handle_deletion_seeds(self):
        dataset_version = DatasetVersion.objects.last()
        collection = Collection.objects.get(name="surf", dataset_version=dataset_version)
        command = self.get_command_instance()
        document_count = collection.document_set.count()
        deletes = [
            seed
            for seed in get_harvest_seeds("surf", make_aware(datetime(year=2019, month=12, day=31)))
            if seed.get("state", "active") != "active"
        ]
        document_deletes = command.handle_deletion_seeds(collection, deletes)
        self.assertEqual(document_deletes, 1)
        self.assertEqual(collection.document_set.count(), document_count,
                         "Did not expect documents to disappear after a delete immediately")
        self.assertEqual(
            collection.document_set.filter(deleted_at__isnull=False).count(),
            document_deletes
        )
