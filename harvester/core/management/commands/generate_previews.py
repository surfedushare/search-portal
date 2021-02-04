import time

from core.management.base import PipelineCommand
from celery import group
from django.db.models import Q

from core.constants import HarvestStages
from core.models import Document, OAIPMHHarvest
from harvester.tasks import generate_browser_preview, generate_pdf_preview, generate_youtube_preview


class Command(PipelineCommand):

    command_name = "generate_previews"

    def handle(self, *args, **options):
        dataset_name = options["dataset"]
        html_documents = Document.objects.filter(
            Q(properties__mime_type="text/html") |
            Q(properties__file_type="pdf")
        ).filter(dataset__name=dataset_name).filter(properties__preview_path=None)
        signatures = self.create_task_signatures(html_documents)

        self.logger.start("previews")
        self.run_jobs_in_group(signatures)

        self.complete_preview_stage(dataset_name)
        self.logger.end("previews")

    def run_jobs_in_group(self, signatures):
        job = group(signatures)
        result = job.apply_async()

        while not result.ready():
            time.sleep(10)

    def create_task_signatures(self, documents):
        return [self.determine_task_signature(document) for document in documents]

    def complete_preview_stage(self, dataset_name):
        OAIPMHHarvest.objects.filter(
            dataset__name=dataset_name,
            stage=HarvestStages.PREVIEW
        ).update(
            stage=HarvestStages.COMPLETE
        )

    def determine_task_signature(self, document):
        file_type = document.properties.get('file_type', None)
        from_youtube = document.properties.get('from_youtube', False)

        if file_type == 'pdf':
            return generate_pdf_preview.s(document.id)

        if from_youtube:
            return generate_youtube_preview.s(document.id)

        return generate_browser_preview.s(document.id)
