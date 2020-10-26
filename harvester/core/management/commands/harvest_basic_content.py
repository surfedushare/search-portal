from datagrowth.resources.http.tasks import send_serie
from datagrowth.resources.shell.tasks import run_serie
from datagrowth.configuration import create_config
from core.management.base import HarvesterCommand
from core.constants import HarvestStages
from core.models import OAIPMHHarvest, FileResource
from edurep.utils import get_edurep_oaipmh_seeds


class Command(HarvesterCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-d', '--dataset', type=str, required=True)

    def download_seed_files(self, seeds):
        download_config = create_config("http_resource", {
            "resource": "core.FileResource",
            "interval_duration": 2000  # 2s between downloads to prevent too many request errors
        })
        self.info("Starting with main content")
        success_main, error_main = send_serie(
            self.progress([[seed["url"]] for seed in seeds]),
            [{} for _ in seeds],
            config=download_config,
            method="get"
        )
        self.info("Errors while downloading main content: {}".format(len(error_main)))
        self.info("Main content downloaded successfully: {}".format(len(success_main)))

        self.info("Starting with package content")
        package_urls = [[seed["package_url"]] for seed in seeds if seed.get("package_url", None)]
        success_package, error_package = send_serie(
            self.progress(package_urls),
            [{} for _ in package_urls],
            config=download_config,
            method="get"
        )
        self.info("Errors while downloading package content: {}".format(len(error_package)))
        self.info("Package content downloaded successfully: {}".format(len(error_main)))

        return success_main + success_package

    def extract_from_seed_files(self, seeds, downloads):
        if not len(seeds):
            return

        tika_config = create_config("shell_resource", {
            "resource": "core.TikaResource",
        })

        self.info("Starting with main content")
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
        self.info("Errors while extracting main texts: {}".format(len(main_error)))
        self.info("Main texts extracted successfully: {}".format(len(main_success)))

        self.info("Starting with package content")
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
        self.info("Errors while extracting package texts: {}".format(len(package_error)))
        self.info("Package texts extracted successfully: {}".format(len(package_success)))

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

        self.header("BASIC CONTENT HARVEST", options)

        # From the Edurep metadata we generate "seeds" that are the starting point for our own data structure
        self.info("Extracting data from sources ...")
        seeds = []
        progress = {}
        for harvest in self.progress(harvest_queryset, total=harvest_queryset.count()):
            set_specification = harvest.source.spec
            harvest_seeds = get_edurep_oaipmh_seeds(
                set_specification,
                harvest.latest_update_at,
                include_deleted=False
            )
            seeds += harvest_seeds
            progress[set_specification] = len(harvest_seeds)
        for set_name, seeds_count in progress.items():
            self.info(f'Amount of extracted results by OAI-PMH for "{set_name}": {seeds_count}')
        self.info("")

        # Download files of all seeds
        self.info("Downloading files ...")
        download_ids = self.download_seed_files(seeds)

        # Process files with Tika to extract data from content
        self.info("Extracting basic content from files ...")
        self.extract_from_seed_files(seeds, download_ids)

        # Finish the basic harvest
        for harvest in harvest_queryset:
            harvest.stage = HarvestStages.BASIC
            harvest.save()
