from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.core.management import call_command

from core.models import Document
from core.tests.factories import DocumentFactory, DatasetFactory, DatasetVersionFactory, HarvestFactory
from core.constants import HarvestStages


PIPELINE_PROCESSOR_TARGET = "core.management.commands.generate_previews.ShellPipelineProcessor"

processor_mock_result = MagicMock()


class TestGeneratePreviews(TestCase):

    @patch(PIPELINE_PROCESSOR_TARGET, return_value=processor_mock_result)
    def test_generate_previews(self, pipeline_processor_target):
        dataset = DatasetFactory.create(name="test")
        dataset_version = DatasetVersionFactory.create(dataset=dataset)
        harvest = HarvestFactory.create(dataset=dataset, stage=HarvestStages.PREVIEW)
        # Documents that will actually get processed
        DocumentFactory.create(dataset_version=dataset_version, mime_type="text/html",
                               from_youtube=True)
        # Other Documents that get ignored due to various reasons
        DocumentFactory.create(dataset_version=dataset_version, mime_type="text/html", analysis_allowed=False,
                               from_youtube=True)
        DocumentFactory.create(dataset_version=dataset_version, mime_type="foo/bar")

        call_command("generate_previews", f"--dataset={dataset.name}")

        pipeline_processor_target.assert_any_call(
            {
                "pipeline_app_label": "core",
                "pipeline_phase": "youtube_preview",
                "pipeline_depends_on": "metadata",
                "batch_size": 100,
                "asynchronous": False,
                "retrieve_data": {
                    "resource": "core.youtubethumbnailresource",
                    "args": ["$.url"],
                    "kwargs": {},
                },
                "contribute_data": {
                    "to_property": "previews",
                    "objective": {
                        "@": "$",
                        "full_size": "$.full_size",
                        "preview": "$.preview",
                        "preview_small": "$.preview_small",
                    }
                }
            }
        )
        self.assertEqual(processor_mock_result.call_count, 1)
        document_count_expectations = (
            Document.objects.filter(properties__from_youtube=True, properties__analysis_allowed=True).count(),
        )
        for arguments, expectation in zip(processor_mock_result.call_args_list, document_count_expectations):
            args, kwargs = arguments
            document_queryset = args[0]
            self.assertEqual(document_queryset.count(), expectation)
            self.assertIs(document_queryset.model, Document)

        harvest.refresh_from_db()
        self.assertEqual(harvest.stage, HarvestStages.COMPLETE)
