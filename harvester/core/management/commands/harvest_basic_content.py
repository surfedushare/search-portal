from datagrowth.resources.http.tasks import send_serie
from datagrowth.resources.shell.tasks import run_serie
from datagrowth.configuration import create_config
from core.management.base import PipelineCommand
from core.constants import HarvestStages
from core.models import Harvest, FileResource
from harvester.utils.extraction import get_harvest_seeds


class Command(PipelineCommand):

    command_name = "harvest_basic_content"

    def download_seed_files(self, phase, seeds):
        download_config = create_config("http_resource", {
            "resource": "core.FileResource"
        })

        main_phase = phase + ".main"
        self.logger.start(main_phase)
        success_main = []
        error_main = 0
        for batch in self.batchify(main_phase, seeds, len(seeds)):
            batch_seeds = list(batch)
            success_batch, error_batch = send_serie(
                [[seed["url"]] for seed in batch_seeds],
                [{} for _ in batch_seeds],
                config=download_config,
                method="get"
            )
            success_main += success_batch
            error_main += len(error_batch)
        self.logger.end(main_phase, success=success_main, fail=error_main)

        return success_main

    def extract_from_seed_files(self, phase, seeds, downloads):
        if not len(seeds):
            return

        tika_config = create_config("shell_resource", {
            "resource": "core.TikaResource",
        })

        main_phase = phase + ".main"
        self.logger.start(main_phase)
        uris = [FileResource.uri_from_url(seed["url"]) for seed in seeds]
        file_resources = FileResource.objects.filter(uri__in=uris, id__in=downloads)
        signed_urls = [
            resource.get_signed_absolute_uri()
            for resource in file_resources
        ]
        success_main = 0
        error_main = 0
        for batch in self.batchify(main_phase, signed_urls, len(signed_urls)):
            batch_urls = [[url] for url in batch if url is not None]
            batch_success, batch_error = run_serie(
                batch_urls,
                [{} for _ in batch_urls],
                config=tika_config
            )
            success_main += len(batch_success)
            error_main += len(batch_error)
        self.logger.end(main_phase, success=success_main, fail=error_main)

    def handle(self, *args, **options):

        dataset_name = options["dataset"]

        harvest_queryset = Harvest.objects.filter(
            dataset__name=dataset_name,
            stage=HarvestStages.NEW
        )
        if not harvest_queryset.exists():
            raise Harvest.DoesNotExist(
                f"There are no scheduled and NEW Harvest objects for '{dataset_name}'"
            )

        self.logger.start("basic")

        # From the Edurep metadata we generate "seeds" that are the starting point for our own data structure
        self.logger.start("basic.sourcing")
        seeds = []
        for harvest in harvest_queryset:
            set_specification = harvest.source.spec
            harvest_seeds = get_harvest_seeds(
                set_specification,
                harvest.latest_update_at,
                include_deleted=False
            )
            seeds += [seed for seed in harvest_seeds if seed['analysis_allowed']]
            self.logger.progress(f'basic.sourcing.{set_specification}', total=harvest_queryset.count(),
                                 success=len(harvest_seeds))

        self.logger.end("basic.sourcing")
        self.logger.start("basic.download")
        download_ids = []

        # Download youtube videos
        phase_name = "basic.download.youtube"
        youtube_videos = [seed for seed in seeds if seed['from_youtube']]
        if len(youtube_videos) > 0:
            self.logger.start(phase_name)
            download_ids += self.download_seed_files(phase_name, youtube_videos)
            self.logger.end(phase_name)

        # Download other seeds
        phase_name = "basic.download.other"
        other_seeds = [seed for seed in seeds if not seed['from_youtube']]
        if len(other_seeds) > 0:
            self.logger.start(phase_name)
            download_ids += self.download_seed_files(phase_name, other_seeds)
            self.logger.end(phase_name)

        self.logger.end(phase_name)
        self.logger.end("basic.download")

        # Process files with Tika to extract data from content
        self.logger.start("basic.extract")
        self.extract_from_seed_files("basic.extract", seeds, download_ids)
        self.logger.end("basic.extract")

        harvest_queryset.update(stage=HarvestStages.BASIC)

        self.logger.end("basic")
