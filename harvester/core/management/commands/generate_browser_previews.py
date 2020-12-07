from core.management.base import HarvesterCommand
from celery import group
from core.models import Document, OAIPMHHarvest
from harvester.tasks.preview import generate_browser_preview
from core.constants import HarvestStages


class Command(HarvesterCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-d', '--dataset', type=str, required=True)

    def handle(self, *args, **options):
        dataset_name = options["dataset"]
        html_documents = Document.objects.filter(properties__mime_type="text/html").filter(dataset__name=dataset_name)
        signatures = self.create_task_signatures(html_documents)
        self.run_jobs_in_group(signatures)
        self.complete_preview_stage(dataset_name)

    def run_jobs_in_group(self, signatures):
        job = group(signatures)
        result = job.apply_async()
        result.join()

    def create_task_signatures(self, documents):
        return [generate_browser_preview.s(document.id) for document in documents]

    def complete_preview_stage(self, dataset_name):
        OAIPMHHarvest.objects.filter(
            dataset__name=dataset_name,
            stage=HarvestStages.PREVIEW
        ).update(
            stage=HarvestStages.COMPLETE
        )
