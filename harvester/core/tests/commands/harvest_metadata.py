from unittest.mock import patch
from datetime import datetime

from django.test import TestCase
from django.core.management import call_command, CommandError
from django.utils.timezone import make_aware

from datagrowth.resources.http.tasks import send
from core.models import Document, Harvest
from core.constants import HarvestStages, Repositories
from core.logging import HarvestLogger
from edurep.tests.factories import EdurepOAIPMHFactory


class TestMetadataHarvest(TestCase):
    """
    This test case represents the scenario where a harvest is started from t=0
    """

    fixtures = ["datasets-new"]

    def setUp(self):
        EdurepOAIPMHFactory.create_common_edurep_responses()
        super().setUp()

    def test_edurep_surf(self):
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


class TestMetadataHarvestWithHistory(TestCase):
    """
    This test case represents the scenario where a harvest from a previous harvest
    """

    fixtures = ["datasets-history"]

    def setUp(self):
        EdurepOAIPMHFactory.create_common_edurep_responses(include_delta=True)
        super().setUp()

    def test_edurep_surf(self):
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
        # Check if Documents got removed correctly
        try:
            Document.objects.get(id=197515)
            self.fail("Old deleted Document did not get removed")
        except Document.DoesNotExist:
            pass
