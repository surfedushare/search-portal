from collections import defaultdict

from django.core.management import CommandError
from django.utils.timezone import now

from datagrowth.resources.http.tasks import send
from datagrowth.configuration import create_config
from core.management.base import HarvesterCommand
from core.constants import HarvestStages
from core.models import Arrangement
from core.models import OAIPMHHarvest


class Command(HarvesterCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-d', '--dataset', type=str, required=True)
        parser.add_argument('-f', '--fake', action="store_true", default=False)

    def prepare_harvest(self, dataset_name):
        Arrangement.objects.filter(deleted_at__isnull=False).delete()
        for harvest in OAIPMHHarvest.objects.filter(dataset__name=dataset_name, stage=HarvestStages.COMPLETE):
            harvest.stage = HarvestStages.NEW
            harvest.latest_update_at = harvest.harvested_at
            harvest.save()

    def handle(self, *args, **options):

        dataset_name = options["dataset"]
        fake = options["fake"]

        if not fake:
            self.prepare_harvest(dataset_name)

        harvest_queryset = OAIPMHHarvest.objects.filter(
            dataset__name=dataset_name,
            stage=HarvestStages.NEW
            # TODO: filter on Edurep
        )
        if not harvest_queryset.exists():
            raise OAIPMHHarvest.DoesNotExist(
                f"There are no NEW OAIPMHHarvest objects for '{dataset_name}'"
            )

        self.header("EDUREP SEEDS HARVEST", options)

        # Calling the Edurep OAI-PMH interface and get the Edurep meta data about learning materials
        self.info("Fetching metadata for sources ...")
        send_config = create_config("http_resource", {
            "resource": "edurep.EdurepOAIPMH",
            "continuation_limit": 1000,
        })
        current_time = now()
        successes = defaultdict(int)
        fails = defaultdict(int)
        for harvest in self.progress(harvest_queryset, total=harvest_queryset.count()):
            set_specification = harvest.source.spec
            scc, err = send(set_specification, f"{harvest.latest_update_at:%Y-%m-%d}", config=send_config, method="get")
            if len(err):
                raise CommandError("Failed to harvest seeds from Edurep OAI-PMH")
            successes[set_specification] += len(scc)
            fails[set_specification] += len(err)
            if not fake:
                harvest.harvested_at = current_time
                harvest.save()
        self.info('Failed OAI-PMH calls: ', fails)
        self.info('Successful OAI-PMH calls: ', successes)
        success_count = sum(successes.values())
        fail_count = sum(fails.values())
        return f'OAI-PMH: {success_count}/{success_count+fail_count}'
