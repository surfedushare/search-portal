from io import StringIO
from unittest.mock import patch, Mock

from django.test import TestCase
from django.core.management import call_command

from core.management.commands.generate_browser_previews import Command as GenerateBrowserPreviewsCommand
from core.tests.factories import DocumentFactory, DatasetFactory, OAIPMHHarvestFactory
from core.constants import HarvestStages


class TestGenerateBrowserReviews(TestCase):
    def get_command_instance(self):
        command = GenerateBrowserPreviewsCommand()
        command.show_progress = False
        command.info = lambda x: x
        return command

    @patch("celery.group.apply_async")
    @patch("harvester.tasks.preview.generate_browser_preview.s")
    def test_calling_jobs_with_html_documents(self, preview_task_mock, apply_async_mock):
        join_mock = Mock()
        apply_async_mock.return_value.join = join_mock
        out = StringIO()
        dataset = DatasetFactory.create(name="test")
        oaipmh_harvest = OAIPMHHarvestFactory.create(dataset=dataset, stage=HarvestStages.PREVIEW)
        document_with_website = DocumentFactory.create(dataset=dataset, properties={"mime_type": "text/html"})
        DocumentFactory.create(dataset=dataset, properties={"mime_type": "foo/bar"})

        call_command(
            "generate_browser_previews", f"--dataset={dataset.name}", "--no-progress", "--no-logger", stdout=out
        )

        preview_task_mock.assert_called_once_with(document_with_website.id)
        apply_async_mock.assert_called()
        join_mock.assert_called()
        oaipmh_harvest.refresh_from_db()
        self.assertEqual(oaipmh_harvest.stage, HarvestStages.COMPLETE)
