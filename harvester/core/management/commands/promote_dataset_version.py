import logging
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.models import Dataset, DatasetVersion


logger = logging.getLogger("harvester")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-d', '--dataset', type=str, default="")
        parser.add_argument('-hv', '--harvester-version', type=str, default=settings.VERSION)
        parser.add_argument('-i', '--dataset-version-id', type=int, default=0)

    def handle(self, *args, **options):

        dataset_version_id = options["dataset_version_id"]
        dataset_name = options["dataset"]
        harvester_version = options["harvester_version"]

        if not dataset_version_id and not dataset_name:
            raise CommandError("Dataset name required if dataset version id is not specified")

        if dataset_version_id:
            dataset_version = DatasetVersion.objects.get(pk=dataset_version_id)
        else:
            dataset = Dataset.objects.get(name=dataset_name)
            dataset_version = dataset.versions.filter(version=harvester_version).last()

        if not dataset_version:
            raise CommandError("Can't find a dataset version that matches input")

        logger.info(f"Promoting: {dataset_version.dataset.name}, {dataset_version.version} (id={dataset_version.id})")

        for index in dataset_version.indices.all():
            logger.info(f"Promoting index { index.remote_name } to latest")
            index.promote_to_latest()

        dataset_version.set_current()

        logger.info("Finished promoting indices")
