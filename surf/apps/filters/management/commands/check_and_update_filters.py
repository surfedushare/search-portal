from django.core.management.base import BaseCommand, CommandError
from surf.apps.filters.utils import check_and_update_mptt_filters


class Command(BaseCommand):
    """
    Command to check and update the mptt filters.
    When there are no filter items in the database this will not do anything.
    When there are only root nodes this will add the appropriate children to those filter items.
    """
    help = 'Updates the filter items through Edurep'

    def handle(self, *args, **options):
        try:
            self.stdout.write('Starting filter update, this may take a minute or two.')
            check_and_update_mptt_filters()
            self.stdout.write(self.style.SUCCESS('Successfully updated the filters from Edurep'))
        except Exception as exc:
            raise CommandError(str(exc))
