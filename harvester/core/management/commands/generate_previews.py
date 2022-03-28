import time

from core.management.base import PipelineCommand

from core.constants import HarvestStages
from core.models import DatasetVersion, Document, Harvest
from core.processors import ShellPipelineProcessor, HttpPipelineProcessor


class Command(PipelineCommand):

    command_name = "generate_previews"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-a', '--async', action="store_true")

    def handle(self, *args, **options):
        dataset_name = options["dataset"]
        dataset_version = DatasetVersion.objects.get_latest_version(dataset_name=dataset_name)
        asynchronous = options["async"]
        results = []

        youtube_documents = Document.objects.filter(
            dataset_version=dataset_version,
            properties__analysis_allowed=True,
            properties__from_youtube=True
        )
        vimeo_documents = Document.objects.filter(
            dataset_version=dataset_version,
            properties__analysis_allowed=True,
            properties__url__startswith="https://vimeo.com"
        )
        youtube_dl_processor = ShellPipelineProcessor({
            "pipeline_app_label": "core",
            "pipeline_phase": "youtube_preview",
            "pipeline_depends_on": "metadata",
            "batch_size": options["batch_size"],
            "asynchronous": asynchronous,
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
        })
        results.append(youtube_dl_processor(youtube_documents))
        results.append(youtube_dl_processor(vimeo_documents))

        pdf_documents = Document.objects.filter(
            dataset_version=dataset_version,
            properties__mime_type="application/pdf",
            properties__analysis_allowed=True
        )
        pdf_processor = HttpPipelineProcessor({
            "pipeline_app_label": "core",
            "pipeline_phase": "pdf_preview",
            "pipeline_depends_on": "metadata",
            "batch_size": options["batch_size"],
            "asynchronous": asynchronous,
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
        })
        results.append(pdf_processor(pdf_documents))

        self.logger.start("previews")
        if asynchronous and len(results):
            while not all([result.ready() for result in results if result]):
                time.sleep(10)
        Harvest.objects \
            .filter(dataset__name=dataset_name, stage=HarvestStages.PREVIEW)\
            .update(stage=HarvestStages.COMPLETE)
        self.logger.end("previews")
