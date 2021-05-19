import os
import logging
from io import StringIO
from invoke import Context

from django.conf import settings
from django.core.management import base, call_command, CommandError
from django.apps import apps
from django.db import models, connection

from datagrowth.utils import get_dumps_path, objects_from_disk
from surfpol.configuration import create_configuration
from harvester.settings import environment
from core.models import Dataset, FileResource
from core.models.resources.basic import file_resource_delete_handler


logger = logging.getLogger("harvester")


class Command(base.LabelCommand):
    """
    A temporary command to load data from S3 bucket as long as harvester can't generate all production data
    """

    resources = [
        "core.FileResource",
        "core.TikaResource",
        "edurep.EdurepOAIPMH"
    ]

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-s', '--skip-download', action="store_true")
        parser.add_argument('-hs', '--harvest-source', type=str)

    def load_resources(self):
        models.signals.post_delete.disconnect(
            file_resource_delete_handler,
            sender=FileResource,
            dispatch_uid="file_resource_delete"
        )
        for resource_model in self.resources:
            model = apps.get_model(resource_model)
            model.objects.all().delete()
            call_command("load_resource", resource_model)
        models.signals.post_delete.connect(
            file_resource_delete_handler,
            sender=FileResource,
            dispatch_uid="file_resource_delete"
        )

    def reset_postgres_sequences(self):
        app_labels = set([resource.split(".")[0] for resource in self.resources])
        for app_label in app_labels:
            out = StringIO()
            call_command("sqlsequencereset", app_label, "--no-color", stdout=out)
            with connection.cursor() as cursor:
                sql = out.getvalue()
                cursor.execute(sql)

    def bulk_create_objects(self, objects):
        obj = objects[0]
        model = type(obj)
        model.objects.bulk_create(objects)

    def handle_label(self, dataset_label, **options):

        skip_download = options["skip_download"]
        harvest_source = options.get("harvest_source", None)
        assert harvest_source or environment.env != "localhost", \
            "Expected a harvest source argument for a localhost environment"
        source_environment = create_configuration(harvest_source, project="harvester") \
            if harvest_source else environment

        # Delete old datasets
        dataset = Dataset.objects.filter(name=dataset_label).last()
        if dataset is not None:
            dataset.harvestsource_set.all().delete()
            dataset.harvest_set.all().delete()
            dataset.delete()

        if harvest_source and not skip_download:
            logger.info(f"Downloading dump file for: {dataset_label}")
            ctx = Context(environment)
            harvester_data_bucket = f"s3://{source_environment.aws.harvest_content_bucket}/datasets/harvester"
            ctx.run(f"aws s3 sync {harvester_data_bucket} {settings.DATAGROWTH_DATA_DIR}")
        logger.info(f"Importing dataset: {dataset_label}")
        for entry in os.scandir(get_dumps_path(Dataset)):
            if entry.is_file() and entry.name.startswith(dataset_label):
                dataset_file = entry.path
                break
        else:
            raise CommandError(f"Can't find a dump file for label: {dataset_label}")

        # Process dump file
        with open(dataset_file, "r") as dump_file:
            for objects in objects_from_disk(dump_file):
                self.bulk_create_objects(objects)

        # Load resources
        self.load_resources()
        self.reset_postgres_sequences()
