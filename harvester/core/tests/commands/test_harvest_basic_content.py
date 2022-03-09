from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.core.management import call_command

from core.constants import HarvestStages
from core.models import Harvest, Collection, Document


PIPELINE_PROCESSOR_TARGET = "core.management.commands.harvest_basic_content.HttpPipelineProcessor"

processor_mock_result = MagicMock()


@override_settings(VERSION="0.0.1")
class TestBasicHarvest(TestCase):

    fixtures = ["datasets-history"]

    def setUp(self):
        Harvest.objects.filter(source__spec="edusources").update(stage=HarvestStages.NEW)
        self.collection = Collection.objects.last()
        super().setUp()

    @patch(PIPELINE_PROCESSOR_TARGET, return_value=processor_mock_result)
    def test_basic_surf(self, pipeline_processor_target):
        # Checking whether end result of the command returned by "handle" matches expectations.
        # The heavy lifting is done by the HttpPipelineProcessor and we check its usage.
        call_command("harvest_basic_content", "--dataset=test")
        pipeline_processor_target.assert_any_call(
            {
                "pipeline_app_label": "core",
                "pipeline_phase": "tika",
                "pipeline_depends_on": "metadata",
                "batch_size": 100,
                "asynchronous": False,
                "retrieve_data": {
                    "resource": "core.httptikaresource",
                    "method": "post",
                    "args": [],
                    "kwargs": {"url": "$.url"},
                },
                "contribute_data": {
                    "objective": {
                        "@": "$",
                        "text": "$.text"
                    }
                }
            }
        )
        pipeline_processor_target.assert_any_call(
            {
                "pipeline_app_label": "core",
                "pipeline_phase": "extruct",
                "pipeline_depends_on": "metadata",
                "batch_size": 100,
                "asynchronous": False,
                "retrieve_data": {
                    "resource": "core.extructresource",
                    "method": "get",
                    "args": ["$.url"],
                    "kwargs": {},
                },
                "contribute_data": {
                    "to_property": "video",
                    "objective": {
                        "@": "$.microdata",
                        "duration": "$.properties.duration",
                        "embed_url": "$.properties.embedUrl"
                    }
                }
            }
        )
        self.assertEqual(processor_mock_result.call_count, 2)
        document_count_expectations = (
            self.collection.documents.count(),
            self.collection.documents.filter(properties__from_youtube=True).count(),
        )
        for arguments, expectation in zip(processor_mock_result.call_args_list, document_count_expectations):
            args, kwargs = arguments
            document_queryset = args[0]
            self.assertEqual(document_queryset.count(), expectation)
            self.assertIs(document_queryset.model, Document)
        # Last but not least we check that the correct EdurepHarvest objects have indeed progressed
        # to prevent repetitious harvests.
        surf_harvest = Harvest.objects.get(source__spec="edusources")
        self.assertEqual(
            surf_harvest.stage,
            HarvestStages.BASIC,
            "edusources set harvest should got updated to stage BASIC to prevent re-harvest in the future"
        )
        edurep_delen_harvest = Harvest.objects.get(source__spec="edurep_delen")
        self.assertEqual(
            edurep_delen_harvest.stage,
            HarvestStages.VIDEO,
            "edurep_delen set harvest got updated to other than VIDEO while we expected it to be ignored"
        )

    def test_basic_invalid_dataset(self):
        # Testing the case where a Dataset does not exist at all
        try:
            call_command("harvest_basic_content", "--dataset=invalid")
            self.fail("harvest_basic_content did not raise for an invalid dataset")
        except Harvest.DoesNotExist:
            pass
        # Testing the case where a Dataset exists, but no harvest tasks are present
        surf_harvest = Harvest.objects.get(source__spec="edusources")
        surf_harvest.stage = HarvestStages.BASIC
        surf_harvest.save()
        try:
            call_command("harvest_basic_content", "--dataset=invalid")
            self.fail("harvest_basic_content did not raise for a dataset without pending harvests")
        except Harvest.DoesNotExist:
            pass
