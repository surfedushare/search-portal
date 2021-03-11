import logging

from django.core.management.base import BaseCommand

from surf.apps.filters.utils import sync_category_filters


logger = logging.getLogger("service")


class Command(BaseCommand):
    """
    Command to check and update the mptt filters.
    When there are no filter items in the database this will not do anything.
    When there are only root nodes this will add the appropriate children to those filter items.
    """
    help = 'Updates the filter items through Edurep'

    def handle(self, *args, **options):
        logger.info('Starting filter update')
        sync_category_filters()
        logger.info('Successfully updated the filters and translations')
