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
            "interval_duration": 1000  # 1s between downloads to prevent too many request errors
        })
        success, error = send_serie(
            self.progress([[seed["url"]] for seed in seeds]),
            [{} for _ in seeds],
            config=download_config,
            method="get"
        )
        self.info("Errors while downloading content: {}".format(len(error)))
        self.info("Content downloaded successfully: {}".format(len(success)))
        return success

    def extract_from_seed_files(self, seeds, downloads):
        if not len(seeds):
            return

        uris = [FileResource.uri_from_url(seed["url"]) for seed in seeds]
        file_resources = FileResource.objects.filter(uri__in=uris, id__in=downloads)

        tika_config = create_config("shell_resource", {
            "resource": "core.TikaResource",
        })
        success, error = run_serie(
            self.progress([[resource.get_absolute_uri()] for resource in file_resources]),
            [{} for _ in file_resources],
            config=tika_config
        )

        self.info("Errors while extracting texts: {}".format(len(error)))
        self.info("Texts extracted successfully: {}".format(len(success)))

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
