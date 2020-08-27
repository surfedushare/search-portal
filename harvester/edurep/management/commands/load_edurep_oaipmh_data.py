import os
from glob import glob
from invoke import Context

from django.conf import settings
from django.core.management import call_command
from django.apps import apps

from harvester.settings import environment
from core.management.base import HarvesterCommand


class Command(HarvesterCommand):
    """
    A command to load EdurepOAIPMH data from S3 bucket.
    This is to prevent local machines from connecting to Edurep themselves (which they can't do)
    """

    resources = [
        "edurep.EdurepOAIPMH"
    ]

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-f', '--force-download', action="store_false")

    def bulk_create_objects(self, objects):
        obj = objects[0]
        model = type(obj)
        model.objects.bulk_create(objects)

    def handle(self, **options):

        force_download = options["force_download"]

        # Look for resource files or download from AWS
        # Use AWS CLI to download because it handles a lot of cases that we don't want to manage ourselves
        dumps_path = os.path.join(settings.DATAGROWTH_DATA_DIR, "edurep", "dumps", "edurepoaipmh")
        os.makedirs(dumps_path, exist_ok=True)
        dump_files = glob(os.path.join(dumps_path, "*"))
        if not len(dump_files) or force_download:
            self.info(f"Downloading dump file for EdurepOAIPMH")
            ctx = Context(environment)
            harvester_data_bucket = "s3://edushare-data/datasets/harvester/edurep"
            ctx.run(f"aws s3 sync {harvester_data_bucket} {settings.DATAGROWTH_DATA_DIR}/edurep")

        for resource_model in self.resources:
            model = apps.get_model(resource_model)
            model.objects.all().delete()
            call_command("load_resource", resource_model)
