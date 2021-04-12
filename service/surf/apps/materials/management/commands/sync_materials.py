import logging
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware

from surf.apps.materials.models import Material


logger = logging.getLogger("service")


class Command(BaseCommand):
    """
    Command to check and update the materials.
    We keep track of materials for metrics mostly.
    """
    help = 'Updates the materials through Elastic Search'

    def handle(self, *args, **options):
        logger.info('Starting materials sync')
        now = make_aware(datetime.utcnow())
        thirty_days_ago = now - timedelta(days=30)
        Material.objects.filter(deleted_at__lte=thirty_days_ago).delete()
        for material in Material.objects.all():
            material.sync_info()
        logger.info('Successfully synced the materials')
