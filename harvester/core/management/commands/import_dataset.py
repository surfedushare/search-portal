from django.core.management import base

from core.management.base import HarvesterCommand
from core.background import celery_import_dataset


class Command(base.LabelCommand, HarvesterCommand):
    """
    A command that calls the import_dataset background task
    Normally this background task runs once a day, but we may want to trigger this manually as well,
    especially during development on AWS
    """

    def handle_label(self, dataset, **options):
        self.info(f"Calling import_dataset outside of schedule for: {dataset}")
        celery_import_dataset(dataset)
