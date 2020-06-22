import os

from django.core.management import base, call_command, CommandError
from django.apps import apps

from datagrowth.utils import get_dumps_path, objects_from_disk
from core.models import Dataset


class Command(base.LabelCommand):
    """
    A temporary command to load data from S3 bucket as long as harvester can't generate all production data
    """

    resources = [
        "edurep.EdurepOAIPMH"
    ]

    def load_resources(self):
        for resource_model in self.resources:
            model = apps.get_model(resource_model)
            model.objects.all().delete()
            call_command("load_resource", resource_model)

    def bulk_create_objects(self, objects):
        obj = objects[0]
        model = type(obj)
        model.objects.bulk_create(objects)

    def handle_label(self, dataset_label, **options):

        # Delete old datasets
        dataset = Dataset.objects.filter(name=dataset_label).last()
        if dataset is not None:
            dataset.delete()

        # Look for data dump file
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
