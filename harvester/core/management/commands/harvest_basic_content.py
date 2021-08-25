import time

from core.management.base import PipelineCommand
from core.constants import HarvestStages
from core.models import DatasetVersion, Harvest
from core.processors import HttpPipelineProcessor


class Command(PipelineCommand):

    command_name = "harvest_basic_content"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-a', '--async', action="store_true")

    def handle(self, *args, **options):

        dataset_name = options["dataset"]
        asynchronous = options["async"]

        harvest_queryset = Harvest.objects.filter(
            dataset__name=dataset_name,
            stage=HarvestStages.NEW
        )
        if not harvest_queryset.exists():
            raise Harvest.DoesNotExist(
                f"There are no scheduled and NEW Harvest objects for '{dataset_name}'"
            )

        self.logger.start("basic")

        # Process files with Tika to extract data from content
        self.logger.start("basic.tika+extruct")
        dataset_version = DatasetVersion.objects.get_latest_version(dataset_name=dataset_name)
        results = []
        for harvest in harvest_queryset:
            collection = dataset_version.collection_set.filter(name=harvest.source.spec).last()
            if not collection:
                continue

            tika_processor = HttpPipelineProcessor({
                "pipeline_app_label": "core",
                "pipeline_phase": "tika",
                "pipeline_depends_on": "metadata",
                "batch_size": options["batch_size"],
                "asynchronous": asynchronous,
                "retrieve_data": {
                    "resource": "core.httptikaresource",
                    "method": "post",
                    "args": [],
                    "kwargs": {"url": "$.url"},
                },
                "contribute_data": {
                    "objective": {
                        "@": "$",
                        "text": "$.text"
                    }
                }
            })
            results.append(tika_processor(collection.documents.all()))

            extruct_processor = HttpPipelineProcessor({
                "pipeline_app_label": "core",
                "pipeline_phase": "extruct",
                "pipeline_depends_on": "metadata",
                "batch_size": options["batch_size"],
                "asynchronous": asynchronous,
                "retrieve_data": {
                    "resource": "core.extructresource",
                    "method": "get",
                    "args": ["$.url"],
                    "kwargs": {},
                },
                "contribute_data": {
                    "to_property": "video",
                    "objective": {
                        "@": "$.microdata",
                        "duration": "$.properties.duration",
                        "embed_url": "$.properties.embedUrl"
                    }
                }
            })
            results.append(extruct_processor(collection.documents.filter(properties__from_youtube=True)))

        if asynchronous and len(results):
            while not all([result.ready() for result in results if result]):
                time.sleep(10)

        self.logger.end("basic.tika+extruct")

        harvest_queryset.update(stage=HarvestStages.BASIC)

        self.logger.end("basic")
