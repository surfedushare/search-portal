import time

from core.management.base import HarvesterCommand
from celery import group
from django.db.models import Q

from core.constants import HarvestStages
from core.models import Document, OAIPMHHarvest
from harvester.tasks import generate_browser_preview, generate_pdf_preview, generate_youtube_preview
from harvester import logger


class Command(HarvesterCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-d', '--dataset', type=str, required=True)

    def handle(self, *args, **options):
        dataset_name = options["dataset"]
        html_documents = Document.objects.filter(
            Q(properties__mime_type="text/html") |
            Q(properties__file_type="pdf")
        ).filter(dataset__name=dataset_name).filter(properties__preview_path=None)
        signatures = self.create_task_signatures(html_documents)

        logger.info(f"Started {len(signatures)} tasks to generate previews", dataset=dataset_name)
        self.run_jobs_in_group(signatures)

        self.complete_preview_stage(dataset_name)
        logger.info("Done generating previews", dataset=dataset_name)

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
