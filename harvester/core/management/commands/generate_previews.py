import time
from core.management.base import HarvesterCommand
from celery import group
from core.models import Document, OAIPMHHarvest
from harvester.tasks import generate_browser_preview, generate_youtube_preview
from core.constants import HarvestStages


class Command(HarvesterCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-d', '--dataset', type=str, required=True)

    def handle(self, *args, **options):
        dataset_name = options["dataset"]
        html_documents = Document.objects.filter(
            properties__mime_type="text/html"
        ).filter(dataset__name=dataset_name).filter(properties__preview_path=None)
        signatures = self.create_task_signatures(html_documents)
        self.run_jobs_in_group(signatures)
        self.complete_preview_stage(dataset_name)

    def run_jobs_in_group(self, signatures):
        self.info(f"Started {len(signatures)} tasks to generate previews")
        job = group(signatures)
        result = job.apply_async()

        while not result.ready():
            time.sleep(10)

        self.info("Done generating previews")

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
        from_youtube = document.properties.get('from_youtube', False)

        if from_youtube:
            return generate_youtube_preview.s(document.id)

        return generate_browser_preview.s(document.id)
