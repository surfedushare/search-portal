import logging

from django.core.management.base import BaseCommand

from metadata.tasks import sync_metadata


logger = logging.getLogger("harvester")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-s', '--site', type=str, default="ho")

    def handle(self, **options):
        logger.info('Starting metadata sync')
        sync_metadata(options["site"])
        logger.info('Done with metadata sync')
