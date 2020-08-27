from unittest.mock import patch
from io import StringIO
from datetime import datetime

from django.test import TestCase
from django.core.management import call_command
from django.utils.timezone import make_aware

from core.models import Dataset, Collection, OAIPMHHarvest
from core.constants import HarvestStages
from core.management.commands.update_dataset import Command as DatasetCommand
from edurep.utils import get_edurep_oaipmh_seeds


GET_EDUREP_OAIPMH_SEEDS_TARGET = "core.management.commands.update_dataset.get_edurep_oaipmh_seeds"
HANDLE_UPSERT_SEEDS_TARGET = "core.management.commands.update_dataset.Command.handle_upsert_seeds"
HANDLE_DELETION_SEEDS_TARGET = "core.management.commands.update_dataset.Command.handle_deletion_seeds"
DUMMY_SEEDS = [
    {"state": "active", "url": "https://www.vn.nl/speciaalmelk-rechtstreeks-koe/", "mime_type": "text/html"},
    {
        "state": "active",
        "url": "http://www.samhao.nl/webopac/MetaDataEditDownload.csp?file=2:145797:1",
        "mime_type": "application/pdf"
    },
    {"state": "deleted", "url": None, "mime_type": None}
]


class TestCreateOrUpdateDatasetNoHistory(TestCase):

    fixtures = ["datasets-new", "surf-oaipmh-1970-01-01"]  # TODO: include later: , "resources"]

    def setUp(self):
        # Moving the VIDEO source to complete to test it gets ignored by the dataset command
        # Setting the stage of the "surf" set harvests to VIDEO
        # The only valid stage for "update_dataset" to act on.
        OAIPMHHarvest.objects.filter(stage=HarvestStages.VIDEO).update(stage=HarvestStages.COMPLETE)
        OAIPMHHarvest.objects.filter(source__spec="surf").update(stage=HarvestStages.VIDEO)

    def get_command_instance(self):
        command = DatasetCommand()
        command.show_progress = False
        command.info = lambda x: x
        return command

    @patch(GET_EDUREP_OAIPMH_SEEDS_TARGET, return_value=DUMMY_SEEDS)
    @patch(HANDLE_UPSERT_SEEDS_TARGET, return_value=[0, 7, 14])
    @patch(HANDLE_DELETION_SEEDS_TARGET, return_value=[1, 3])
    def test_dataset(self, deletion_target, upsert_target, seeds_target):
        # Checking whether end result of the command returned by "handle" matches expectations.
        # We'd expect the command to get seeds from get_edurep_oaipmh_seeds function.
        # After that the modifications to the dataset are done by two methods named:
        # handle_upsert_seeds and handle_deletion_seeds.
        # We'll test those separately, but check if they get called with the seeds returned by get_edurep_oaipmh_seeds
        out = StringIO()
        call_command("update_dataset", "--dataset=test", "--no-progress", "--no-logger", stdout=out)
        # Asserting usage of get_edurep_oaipmh_seeds
        seeds_target.assert_called_once_with("surf", make_aware(datetime(year=1970, month=1, day=1)))
        # Asserting usage of download_seed_files
        upsert_target.assert_called_once()
        args, kwargs = upsert_target.call_args
        self.assertIsInstance(args[0], Collection)
        self.assertEqual(args[1], DUMMY_SEEDS[:-1])
        # And then usage of extract_from_seeds
        deletion_target.assert_called_once()
        args, kwargs = deletion_target.call_args
        self.assertIsInstance(args[0], Collection)
        self.assertEqual(args[1], DUMMY_SEEDS[-1:])
        # Last but not least we check that the correct EdurepHarvest objects have indeed progressed
        # to prevent repetitious harvests.
        surf_harvest = OAIPMHHarvest.objects.get(source__spec="surf")
        self.assertEqual(
            surf_harvest.stage,
            HarvestStages.COMPLETE,
            "surf set harvest should got updated to stage BASIC to prevent re-harvest in the future"
        )
        edurep_delen_harvest = OAIPMHHarvest.objects.get(source__spec="edurep_delen")
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
        except Dataset.DoesNotExist:
            pass
        # Testing the case where a Dataset exists, but no harvest tasks are present
        surf_harvest = OAIPMHHarvest.objects.get(source__spec="surf")
        surf_harvest.stage = HarvestStages.BASIC
        surf_harvest.save()
        try:
            call_command("update_dataset", "--dataset=test")
            self.fail("update_dataset did not raise for a dataset without pending harvests")
        except OAIPMHHarvest.DoesNotExist:
            pass

    def test_handle_upsert_seeds(self):
        dataset = Dataset.objects.last()
        collection = Collection.objects.create(name="surf", dataset=dataset)
        command = self.get_command_instance()
        upserts = [
            seed
            for seed in get_edurep_oaipmh_seeds("surf", make_aware(datetime(year=1970, month=1, day=1)))
            if seed.get("state", "active") == "active"
        ]
        skipped, dumped, documents_count = command.handle_upsert_seeds(collection, upserts)
        # When dealing with an entirely new Dataset
        # Then the arrangement count and document count should equal output of handle_upsert_seeds
        self.assertEqual(collection.arrangement_set.count(), dumped)
        self.assertEqual(collection.document_set.count(), documents_count)

    def test_handle_deletion_seeds(self):
        dataset = Dataset.objects.last()
        collection = Collection.objects.create(name="surf", dataset=dataset)
        command = self.get_command_instance()
        deletes = [
            seed
            for seed in get_edurep_oaipmh_seeds("surf", make_aware(datetime(year=1970, month=1, day=1)))
            if seed.get("state", "active") != "active"
        ]
        # Basically we're testing that deletion seeds are not triggering errors when their targets do not exist.
        command.handle_deletion_seeds(collection, deletes)
        self.assertEqual(collection.document_set.count(), 0)
        self.assertEqual(collection.arrangement_set.count(), 0)


class TestCreateOrUpdateDatasetWithHistory(TestCase):

    fixtures = ["datasets-history", "surf-oaipmh-2020-01-01"]  # TODO: include later: , "resources"]

    def setUp(self):
        # Setting the stage of the "surf" set harvests to VIDEO.
        # The only valid stage for "update_dataset" to act on.
        OAIPMHHarvest.objects.filter(source__spec="surf").update(stage=HarvestStages.VIDEO)

    def get_command_instance(self):
        command = DatasetCommand()
        command.show_progress = False
        command.info = lambda x: x
        return command

    def test_handle_upsert_seeds(self):
        dataset = Dataset.objects.last()
        collection = Collection.objects.get(name="surf", dataset=dataset)
        command = self.get_command_instance()
        # Checking the state before the test
        arrangement_count = collection.arrangement_set.count()
        document_count = collection.document_set.count()
        vortex_queryset = dataset.documents.filter(properties__title="Using a Vortex | Wageningen UR")
        handson_queryset = dataset.documents.filter(
            properties__title="Hands-on exercise based on WEKA - Tuning and Testing"
        )
        self.assertEqual(vortex_queryset.count(), 1, "Expected the start state to contain 'Using a Vortex'")
        self.assertEqual(handson_queryset.count(), 1, "Expected the start state to contain 'Hands-on exercise'")
        for doc in dataset.documents.all():
            self.assertEqual(doc.created_at, doc.modified_at, f"Document is unexpectedly updated: {doc.id}")
        for arrangement in dataset.arrangement_set.all():
            self.assertEqual(
                arrangement.created_at, arrangement.modified_at,
                f"Arrangement is unexpectedly updated: {arrangement.id}"
            )
        # Perform the test
        upserts = [
            seed
            for seed in get_edurep_oaipmh_seeds("surf", make_aware(datetime(year=2019, month=12, day=31)))
            if seed.get("state", "active") == "active"
        ]
        skipped, dumped, documents_count = command.handle_upsert_seeds(collection, upserts)
        # Checking the state after the test
        self.assertEqual(skipped, 0)
        self.assertEqual(collection.arrangement_set.count(), arrangement_count+2,
                         "Upsert seeds should have added 2 Arrangements")
        self.assertEqual(collection.document_set.count(), document_count+2)
        # TODO: bring back the asserts for video transcriptions once they work through Amber
        # Videos normally contain multiple documents, because they have multiple file types (HTML and video)
        # But now only HTML is supported
        # START VIDEO CONTENT
        vortex_updateset = dataset.documents.filter(properties__title="Using a Vortex (responsibly) | Wageningen UR")
        self.assertEqual(vortex_updateset.count(), 1)
        self.assertEqual(vortex_queryset.count(), 0)
        # END VIDEO CONTENT
        handson_updateset = dataset.documents.filter(
            properties__title="Hands-off exercise based on WEKA - Tuning and Testing"
        )
        self.assertEqual(handson_updateset.count(), 1)
        self.assertEqual(handson_queryset.count(), 0)
        update_ids = set()
        for update in vortex_updateset:
            self.assertNotEqual(update.created_at, update.modified_at,
                                f"Document is unexpectedly not updated: {update.id}")
            self.assertNotEqual(update.arrangement.created_at, update.arrangement.modified_at,
                                f"Arrangement of document is unexpectedly not updated: {update.id}")
            update_ids.add(update.id)
        for update in handson_updateset:
            self.assertNotEqual(update.created_at, update.modified_at,
                                f"Document is unexpectedly not updated: {update.id}")
            self.assertNotEqual(update.arrangement.created_at, update.arrangement.modified_at,
                                f"Arrangement of document is unexpectedly not updated: {update.id}")
            update_ids.add(update.id)
        not_updated = dataset.documents.exclude(id__in=update_ids)
        self.assertNotEqual(not_updated.count(), 0)
        for not_update in not_updated:
            self.assertEqual(
                not_update.created_at.replace(microsecond=0), not_update.modified_at.replace(microsecond=0),
                f"Document is unexpectedly updated after upsert: {not_update.id}"
            )

    def test_handle_empty_upsert_seeds(self):
        # TODO: implement
        self.skipTest("currently all seeds are empty")

    def test_handle_deletion_seeds(self):
        dataset = Dataset.objects.last()
        collection = Collection.objects.get(name="surf", dataset=dataset)
        command = self.get_command_instance()
        arrangement_count = collection.arrangement_set.count()
        document_count = collection.document_set.count()
        deletes = [
            seed
            for seed in get_edurep_oaipmh_seeds("surf", make_aware(datetime(year=2019, month=12, day=31)))
            if seed.get("state", "active") != "active"
        ]
        arrangement_deletes, document_deletes = command.handle_deletion_seeds(collection, deletes)
        self.assertEqual(arrangement_deletes, 1)
        self.assertEqual(document_deletes, 1)
        self.assertEqual(collection.arrangement_set.count(), arrangement_count,
                         "Did not expect arrangements to disappear after a delete")
        self.assertEqual(collection.arrangement_set.filter(deleted_at__isnull=False).count(), arrangement_deletes)
        self.assertEqual(collection.document_set.count(), document_count - document_deletes)
