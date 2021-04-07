import time

from core.management.base import PipelineCommand
from celery import group
from django.db.models import Q

from core.constants import HarvestStages
from core.models import DatasetVersion, Document, Harvest
from core.tasks import generate_browser_preview, generate_pdf_preview, generate_youtube_preview


class Command(PipelineCommand):

    command_name = "generate_previews"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-f', '--fake', action="store_true", default=False)

    def handle(self, *args, **options):
        dataset_name = options["dataset"]
        dataset_version = DatasetVersion.objects.filter(dataset__name=dataset_name, is_current=True).last()
        fake = options["fake"]
        html_documents = Document.objects \
            .filter(
                Q(properties__mime_type="text/html") |
                Q(properties__file_type="pdf")
            ) \
            .filter(dataset_version=dataset_version) \
            .filter(properties__preview_path=None) \
            .filter(properties__analysis_allowed=True)
        documents_count = html_documents.count()

        signatures = [self.determine_task_signature(document, documents_count) for document in html_documents]

        self.logger.start("previews")
        if not fake:
            self.run_jobs_in_group(signatures)

        self.complete_preview_stage(dataset_name)
        self.logger.end("previews")

    def run_jobs_in_group(self, signatures):
        job = group(signatures)
        result = job.apply_async()

        while not result.ready():
            time.sleep(10)

    def complete_preview_stage(self, dataset_name):
        Harvest.objects.filter(
            dataset__name=dataset_name,  # REFACTOR: needs more filtering
            stage=HarvestStages.PREVIEW
        ).update(
            stage=HarvestStages.COMPLETE
        )

    def determine_task_signature(self, document, total):
        file_type = document.properties.get('file_type', None)
        from_youtube = document.properties.get('from_youtube', False)

        if file_type == 'pdf':
            return generate_pdf_preview.s(document.id, total)

        if from_youtube:
            return generate_youtube_preview.s(document.id, total)

        return generate_browser_preview.s(document.id, total)
