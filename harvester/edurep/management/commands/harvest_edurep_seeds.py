from collections import defaultdict
from harvester import logger

from django.core.management import CommandError
from django.utils.timezone import now
from datagrowth.resources.http.tasks import send
from datagrowth.configuration import create_config

from core.management.base import HarvesterCommand
from core.constants import HarvestStages
from core.models import Arrangement, OAIPMHHarvest, OAIPMHRepositories


class Command(HarvesterCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-d', '--dataset', type=str, required=True)
        parser.add_argument('-f', '--fake', action="store_true", default=False)

    def prepare_harvest(self, dataset_name):
        logger.debug("Deleting all arrangements")
        Arrangement.objects.filter(deleted_at__isnull=False).delete()
        harvest_queryset = OAIPMHHarvest.objects.filter(
            dataset__name=dataset_name,
            stage=HarvestStages.COMPLETE,
            source__repository=OAIPMHRepositories.EDUREP
        )
        for harvest in harvest_queryset:
            logger.debug(f"Setting harvest stage to NEW for '{harvest.source.name}'", dataset=dataset_name)
            harvest.stage = HarvestStages.NEW
            harvest.latest_update_at = harvest.harvested_at
            harvest.save()

    def harvest_seeds(self, harvest, current_time, fake):
        send_config = create_config("http_resource", {
            "resource": "edurep.EdurepOAIPMH",
            "continuation_limit": 1000,
        })

        set_specification = harvest.source.spec
        scc, err = send(set_specification, f"{harvest.latest_update_at:%Y-%m-%d}", config=send_config, method="get")

        if len(err):
            raise CommandError("Failed to harvest seeds from Edurep OAI-PMH")

        if not fake:
            harvest.harvested_at = current_time
            harvest.save()

        return len(scc), len(err)

    def handle(self, *args, **options):
        dataset_name = options["dataset"]
        fake = options["fake"]

        logger.info(
            f"Started harvesting of edurep seeds for dataset '{dataset_name}', fake: {fake}",
            dataset=dataset_name
        )

        if not fake:
            self.prepare_harvest(dataset_name)

        harvest_queryset = OAIPMHHarvest.objects.filter(
            dataset__name=dataset_name,
            stage=HarvestStages.NEW,
            source__repository=OAIPMHRepositories.EDUREP
        )
        if not harvest_queryset.exists():
            raise OAIPMHHarvest.DoesNotExist(
                f"There are no NEW OAIPMHHarvest objects for '{dataset_name}'"
            )

        # Calling the Edurep OAI-PMH interface and get the Edurep meta data about learning materials
        logger.info("Fetching metadata for sources ...")

        current_time = now()
        successes = defaultdict(int)
        fails = defaultdict(int)

        for harvest in harvest_queryset:
            success_count, error_count = self.harvest_seeds(harvest, current_time, fake)
            set_specification = harvest.source.spec
            successes[set_specification] += success_count
            fails[set_specification] += error_count
            logger.debug(
                f"Fetched metadata for source '{set_specification}' with name '{harvest.source.name}'",
                dataset=dataset_name,
                aggregate={"success": success_count, "failed": error_count}
            )

        total_success_count = sum(successes.values())
        total_fail_count = sum(fails.values())

        logger.info(
            f"Finished harvesting edurep seeds, "
            f"successful OAI-PMG call: '{total_success_count}', failed OAI-PMH calls: '{total_fail_count}'",
            aggregate={"success": total_success_count, "failed": total_fail_count}
        )

        return f'OAI-PMH: {total_success_count}/{total_success_count + total_fail_count}'
