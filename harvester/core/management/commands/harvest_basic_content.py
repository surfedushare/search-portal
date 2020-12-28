from itertools import chain

from datagrowth.resources.http.tasks import send_serie
from datagrowth.resources.shell.tasks import run_serie
from datagrowth.configuration import create_config
from core.management.base import HarvesterCommand
from core.constants import HarvestStages
from core.models import OAIPMHHarvest, FileResource
from edurep.utils import get_edurep_oaipmh_seeds
from harvester import logger


class Command(HarvesterCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-d', '--dataset', type=str, required=True)

    def download_seed_files(self, seeds, interval=0, dataset=None):
        download_config = create_config("http_resource", {
            "resource": "core.FileResource",
            "interval_duration": interval
        })

        logger.info("Starting with main content", dataset=dataset)
        success_main, error_main = send_serie(
            self.progress([[seed["url"]] for seed in seeds]),
            [{} for _ in seeds],
            config=download_config,
            method="get"
        )

        logger.info(f"Errors while downloading main content: {len(error_main)}", dataset=dataset)
        logger.info(f"Main content downloaded successfully: {len(success_main)}", dataset=dataset)

        logger.info("Starting with package content")
        package_urls = [[seed["package_url"]] for seed in seeds if seed.get("package_url", None)]
        success_package, error_package = send_serie(
            self.progress(package_urls),
            [{} for _ in package_urls],
            config=download_config,
            method="get"
        )
        logger.info(f"Errors while downloading package content: {len(error_package)}", dataset=dataset)
        logger.info(f"Package content downloaded successfully: {len(success_package)}", dataset=dataset)

        return success_main + success_package

    def extract_from_seed_files(self, seeds, downloads, dataset=None):
        if not len(seeds):
            return

        tika_config = create_config("shell_resource", {
            "resource": "core.TikaResource",
        })

        logger.info("Starting with main content", dataset=dataset)
        uris = [FileResource.uri_from_url(seed["url"]) for seed in seeds]
        file_resources = FileResource.objects.filter(uri__in=uris, id__in=downloads)
        signed_urls = [
            resource.get_signed_absolute_uri()
            for resource in file_resources
        ]
        main_success, main_error = run_serie(
            self.progress([[url] for url in signed_urls if url is not None]),
            [{} for _ in file_resources],
            config=tika_config
        )
        logger.info(f"Errors while extracting main texts: {main_error}", dataset=dataset)
        logger.info(f"Main texts extracted successfully: {main_success}", dataset=dataset)

        logger.info("Starting with package content")
        uris = [FileResource.uri_from_url(seed["package_url"]) for seed in seeds if seed.get("package_url", None)]
        file_resources = FileResource.objects.filter(uri__in=uris, id__in=downloads)
        signed_urls = [
            resource.get_signed_absolute_uri()
            for resource in file_resources
        ]
        package_success, package_error = run_serie(
            self.progress([[url] for url in signed_urls if url is not None]),
            [{} for _ in file_resources],
            config=tika_config
        )
        logger.info("Errors while extracting package texts: {package_error}", dataset=dataset)
        logger.info("Package texts extracted successfully: {package_success}", dataset=dataset)

    def generate_seeds(self, harvest, dataset_name):
        logger.debug(f"Getting edurep OAI-PMH seeds for '{harvest.source.spec}'", dataset=dataset_name)
        set_specification = harvest.source.spec
        harvest_seeds = get_edurep_oaipmh_seeds(
            set_specification,
            harvest.latest_update_at,
            include_deleted=False
        )
        logger.info(
            f'Amount of extracted results by OAI-PMH for "{set_specification}": {len(harvest_seeds)}',
            dataset=dataset_name
        )

        return [seed for seed in harvest_seeds if seed['analysis_allowed']]

    def handle(self, *args, **options):

        dataset_name = options["dataset"]

        harvest_queryset = OAIPMHHarvest.objects.filter(
            dataset__name=dataset_name,
            stage=HarvestStages.NEW
        )
        if not harvest_queryset.exists():
            raise OAIPMHHarvest.DoesNotExist(
                f"There are no scheduled and NEW OAIPMHHarvest objects for '{dataset_name}'"
            )

        logger.info(f"Starting basic content harvest for dataset '{dataset_name}'", dataset=dataset_name)

        # From the Edurep metadata we generate "seeds" that are the starting point for our own data structure
        logger.info("Extracting data from sources...", dataset=dataset_name)
        seeds = list(chain.from_iterable([self.generate_seeds(harvest, dataset_name) for harvest in harvest_queryset]))

        download_ids = []

        # Download youtube videos
        youtube_videos = [seed for seed in seeds if seed['from_youtube']]
        if len(youtube_videos) > 0:
            logger.info("Downloading youtube videos...", dataset=dataset_name)
            download_ids = download_ids + self.download_seed_files(youtube_videos, 2000, dataset=dataset_name)

        # Download other seeds
        other_seeds = [seed for seed in seeds if not seed['from_youtube']]
        if len(other_seeds) > 0:
            logger.info("Downloading other seeds...", dataset=dataset_name)
            download_ids = download_ids + self.download_seed_files(other_seeds, dataset=dataset_name)

        # Process files with Tika to extract data from content
        logger.info("Extracting basic content from files...")
        self.extract_from_seed_files(seeds, download_ids, dataset=dataset_name)

        harvest_queryset.update(stage=HarvestStages.BASIC)

        logger.debug("Finished harvesting of basic content.", dataset=dataset_name)
