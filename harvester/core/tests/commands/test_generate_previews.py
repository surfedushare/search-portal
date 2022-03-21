from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.core.management import call_command

from core.models import Document
from core.tests.factories import DocumentFactory, DatasetFactory, DatasetVersionFactory, HarvestFactory
from core.constants import HarvestStages

SHELL_PIPELINE_PROCESSOR_TARGET = "core.management.commands.generate_previews.ShellPipelineProcessor"
HTTP_PIPELINE_PROCESSOR_TARGET = "core.management.commands.generate_previews.HttpPipelineProcessor"

shell_mock_result = MagicMock()
http_mock_result = MagicMock()


@override_settings(VERSION="0.0.1")
class TestGeneratePreviews(TestCase):

    def setUp(self):
        super().setUp()
        self.dataset = DatasetFactory.create(name="test")
        dataset_version = DatasetVersionFactory.create(dataset=self.dataset)
        self.harvest = HarvestFactory.create(dataset=self.dataset, stage=HarvestStages.PREVIEW)
        # Documents that will actually get processed
        DocumentFactory.create(dataset_version=dataset_version, mime_type="text/html",
                               from_youtube=True)
        DocumentFactory.create(dataset_version=dataset_version, mime_type="application/pdf")
        # Other Documents that get ignored due to various reasons
        DocumentFactory.create(dataset_version=dataset_version, mime_type="text/html", analysis_allowed=False,
                               from_youtube=True)
        DocumentFactory.create(dataset_version=dataset_version, mime_type="application/pdf", analysis_allowed=False)
        DocumentFactory.create(dataset_version=dataset_version, mime_type="foo/bar")

    @patch(SHELL_PIPELINE_PROCESSOR_TARGET, return_value=shell_mock_result)
    def test_generate_youtube_previews(self, pipeline_processor_target):

        call_command("generate_previews", f"--dataset={self.dataset.name}")

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
        self.assertEqual(shell_mock_result.call_count, 2)
        document_count_expectations = (
            Document.objects.filter(properties__from_youtube=True, properties__analysis_allowed=True).count(),
            0  # No Vimeo Documents in the test set
        )
        for arguments, expectation in zip(shell_mock_result.call_args_list, document_count_expectations):
            args, kwargs = arguments
            document_queryset = args[0]
            self.assertEqual(document_queryset.count(), expectation)
            self.assertIs(document_queryset.model, Document)

        self.harvest.refresh_from_db()
        self.assertEqual(self.harvest.stage, HarvestStages.COMPLETE)

    @patch(HTTP_PIPELINE_PROCESSOR_TARGET, return_value=http_mock_result)
    def test_generate_pdf_previews(self, pipeline_processor_target):

        call_command("generate_previews", f"--dataset={self.dataset.name}")

        pipeline_processor_target.assert_any_call(
            {
                "pipeline_app_label": "core",
                "pipeline_phase": "pdf_preview",
                "pipeline_depends_on": "metadata",
                "batch_size": 100,
                "asynchronous": False,
                "retrieve_data": {
                    "resource": "core.pdfthumbnailresource",
                    "method": "get",
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
        self.assertEqual(http_mock_result.call_count, 1)
        document_count_expectations = Document.objects \
            .filter(properties__mime_type="application/pdf", properties__analysis_allowed=True) \
            .count()

        for arguments, expectation in zip(http_mock_result.call_args_list, [document_count_expectations]):
            args, kwargs = arguments
            document_queryset = args[0]
            self.assertEqual(document_queryset.count(), expectation)
            self.assertIs(document_queryset.model, Document)

        self.harvest.refresh_from_db()
        self.assertEqual(self.harvest.stage, HarvestStages.COMPLETE)
