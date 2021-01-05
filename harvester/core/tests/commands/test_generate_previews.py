from io import StringIO
from unittest.mock import patch, Mock

from django.test import TestCase
from django.core.management import call_command

from core.management.commands.generate_previews import Command as GeneratePreviewsCommand
from core.tests.factories import DocumentFactory, DatasetFactory, OAIPMHHarvestFactory
from core.constants import HarvestStages


class TestGeneratePreviews(TestCase):
    def get_command_instance(self):
        command = GeneratePreviewsCommand()
        command.show_progress = False
        command.info = lambda x: x
        return command

    @patch("celery.group.apply_async")
    @patch("harvester.tasks.generate_browser_preview.s")
    @patch("harvester.tasks.generate_youtube_preview.s")
    @patch("harvester.tasks.generate_pdf_preview.s")
    def test_calling_jobs_with_html_documents(self, pdf_mock, youtube_task_mock, preview_task_mock, apply_async_mock):
        ready_mock = Mock()
        ready_mock.return_value = True
        apply_async_mock.return_value.ready = ready_mock
        out = StringIO()
        dataset = DatasetFactory.create(name="test")
        oaipmh_harvest = OAIPMHHarvestFactory.create(dataset=dataset, stage=HarvestStages.PREVIEW)
        document_with_website = DocumentFactory.create(dataset=dataset, mime_type="text/html")
        document_from_youtube = DocumentFactory.create(dataset=dataset, mime_type="text/html", from_youtube=True)
        pdf_document = DocumentFactory.create(dataset=dataset, mime_type="application/pdf", file_type="pdf")
        DocumentFactory.create(dataset=dataset, mime_type="foo/bar")
        DocumentFactory.create(dataset=dataset, mime_type="text/html", preview_path="previews/8")

        call_command(
            "generate_previews", f"--dataset={dataset.name}", "--no-progress", "--no-logger", stdout=out
        )

        preview_task_mock.assert_called_once_with(document_with_website.id)
        youtube_task_mock.assert_called_once_with(document_from_youtube.id)
        pdf_mock.assert_called_once_with(pdf_document.id)
        apply_async_mock.assert_called()
        ready_mock.assert_called()
        oaipmh_harvest.refresh_from_db()
        self.assertEqual(oaipmh_harvest.stage, HarvestStages.COMPLETE)
