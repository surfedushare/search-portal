import os
from io import StringIO
from glob import glob
from invoke import Context

from django.conf import settings
from django.core.management import base, call_command, CommandError
from django.apps import apps
from django.db import models, connection

from datagrowth.utils import get_dumps_path, objects_from_disk
from harvester.settings import environment
from core.management.base import HarvesterCommand
from core.models import Dataset, ElasticIndex, FileResource
from core.models.resources.basic import file_resource_delete_handler


class Command(base.LabelCommand, HarvesterCommand):
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
            call_command("sqlsequencereset", app_label, stdout=out)
            with connection.cursor() as cursor:
                cursor.execute(out.getvalue())

    def bulk_create_objects(self, objects):
        obj = objects[0]
        model = type(obj)
        model.objects.bulk_create(objects)

    def handle_label(self, dataset_label, **options):

        skip_download = options["skip_download"]

        # Delete old datasets
        dataset = Dataset.objects.filter(name=dataset_label).last()
        if dataset is not None:
            dataset.oaipmhset_set.all().delete()
            dataset.oaipmhharvest_set.all().delete()
            dataset.delete()

        # Look for data dump file or download from AWS
        # Use AWS CLI here because it handles a lot of cases that we don't want to manage ourselves
        # especially in this throw away command
        dumps_path = os.path.join(settings.DATAGROWTH_DATA_DIR, "core", "dumps", "dataset")
        os.makedirs(dumps_path, exist_ok=True)
        dump_files = glob(os.path.join(dumps_path, f"{dataset_label}*"))
        if not len(dump_files) and not skip_download:
            self.info(f"Downloading dump file for: {dataset_label}")
            ctx = Context(environment)
            harvester_data_bucket = "s3://edushare-data/datasets/harvester"
            ctx.run(f"aws s3 sync {harvester_data_bucket} {settings.DATAGROWTH_DATA_DIR}")
        self.info(f"Importing dataset: {dataset_label}")
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

        # Migrate indices to 7.0
        ElasticIndex.objects.all().update(configuration="")
