import os
from glob import glob
from invoke import Context

from django.conf import settings
from django.core.management import call_command
from django.apps import apps

from project.configuration import create_configuration
from core.management.base import PipelineCommand


class Command(PipelineCommand):
    """
    A command to load EdurepOAIPMH data from S3 bucket.
    This is to prevent local machines from connecting to Edurep themselves (which they can't do).
    Also we want dev and acc environment to stay away from connecting to Edurep (on their request).
    """

    command_name = "load_edurep_oaipmh_data"

    resources = [
        "edurep.EdurepOAIPMH"
    ]

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-f', '--force-download', action="store_false")
        parser.add_argument('-s', '--source', type=str, required=True)

    def handle(self, **options):

        force_download = options["force_download"]
        source = options["source"]
        source_environment = create_configuration(source, service="harvester")

        # Look for resource files or download from AWS
        # Use AWS CLI to download because it handles a lot of cases that we don't want to manage ourselves
        dumps_path = os.path.join(settings.DATAGROWTH_DATA_DIR, "edurep", "dumps", "edurepoaipmh")
        os.makedirs(dumps_path, exist_ok=True)
        dump_files = glob(os.path.join(dumps_path, "*"))
        if not len(dump_files) or force_download:
            self.logger.info("Downloading dump file for EdurepOAIPMH")
            ctx = Context(source_environment)
            harvester_data_bucket = f"s3://{ctx.config.aws.harvest_content_bucket}/datasets/harvester/edurep"
            ctx.run(f"aws s3 sync --no-progress {harvester_data_bucket} {settings.DATAGROWTH_DATA_DIR}/edurep")

        for resource_model in self.resources:
            model = apps.get_model(resource_model)
            model.objects.all().delete()
            call_command("load_resource", resource_model)
