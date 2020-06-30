import logging
from django.db.models import Count
from django.core.management.base import BaseCommand
from django.core.management import call_command

from surf.apps.users.models import SessionToken

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        call_command("clearsessions", *args, **options)
        SessionToken.objects.annotate(num_sessions=Count("sessions")).filter(num_sessions=0).delete()
        logger.info('Executed clearlogins succesfully')
