import logging

from django.core.management.base import BaseCommand

from metadata.tasks import sync_metadata


logger = logging.getLogger("harvester")


class Command(BaseCommand):

    def handle(self, **options):
        logger.info('Starting metadata sync')
        sync_metadata()
        logger.info('Done with metadata sync')
