from django.core.management import CommandError
from django.utils.timezone import now
from datagrowth.resources.http.tasks import send
from datagrowth.configuration import create_config

from core.management.base import PipelineCommand
from core.constants import HarvestStages
from core.models import OAIPMHHarvest, OAIPMHRepositories


class Command(PipelineCommand):

    command_name = "harvest_metadata"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-r', '--repository', action="store", default=OAIPMHRepositories.EDUREP)
        parser.add_argument('-p', '--promote', action="store_true")

    def harvest_seeds(self, harvest, current_time):
        send_config = create_config("http_resource", {
            "resource": harvest.source.repository,
            "continuation_limit": 1000,
        })

        set_specification = harvest.source.spec
        scc, err = send(set_specification, f"{harvest.latest_update_at:%Y-%m-%d}", config=send_config, method="get")

        if len(err):
            raise CommandError("Failed to harvest seeds from Edurep OAI-PMH")

        harvest.harvested_at = current_time
        harvest.save()

        return len(scc), len(err)

    def handle(self, *args, **options):

        dataset_name = options["dataset"]
        repository_resource = options["repository"]

        self.logger.start("seeds")

        harvest_queryset = OAIPMHHarvest.objects.filter(
            dataset__name=dataset_name,
            stage=HarvestStages.NEW,
            source__repository=repository_resource
        )
        if not harvest_queryset.exists():
            raise OAIPMHHarvest.DoesNotExist(
                f"There are no NEW OAIPMHHarvest objects for '{dataset_name}'"
            )

        # Calling the Edurep OAI-PMH interface and get the Edurep meta data about learning materials
        self.logger.start("seeds.metadata")

        current_time = now()
        total_success_count = 0
        total_fail_count = 0
        sources_count = harvest_queryset.count()

        for harvest in harvest_queryset:
            success_count, error_count = self.harvest_seeds(harvest, current_time)
            set_specification = harvest.source.spec
            total_success_count += success_count
            total_fail_count += error_count
            self.logger.progress(f"seed.metadata.{set_specification}", total=sources_count, success=success_count,
                                 fail=error_count)

        self.logger.end("seeds.metadata", total_success_count, total_fail_count)
        self.logger.end("seeds")
