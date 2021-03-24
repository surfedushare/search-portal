import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from surf.apps.filters.utils import sync_category_filters


logger = logging.getLogger("service")


class Command(BaseCommand):
    """
    Command to check and update the mptt filters.
    When there are no filter items in the database this will not do anything.
    When there are only root nodes this will add the appropriate children to those filter items.
    """
    help = 'Updates the filter items through Elastic Search aggregations'

    def handle(self, *args, **options):
        logger.info('Starting filter update')
        has_new_filters = sync_category_filters()
        if has_new_filters and settings.ENABLE_ADMINISTRATIVE_EMAILS:
            send_mail(
                'Nieuwe Zoekportaal filters en/of filter vertalingen',
                'Login op de admin om de filters zichtbaar te maken en vertalingen goed te keuren.',
                'noreply@edusources.nl',
                ['edusources-team@surf.nl']
            )
        logger.info('Successfully updated the filters and translations')
