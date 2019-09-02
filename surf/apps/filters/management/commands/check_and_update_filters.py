from django.core.management.base import BaseCommand, CommandError
from surf.apps.filters.utils import check_and_update_mptt_filters


class Command(BaseCommand):
    help = 'Updates the filter items through Edurep'

    def handle(self, *args, **options):
        try:
            self.stdout.write('Starting filter update, this may take a minute or two.')
            check_and_update_mptt_filters()
            self.stdout.write(self.style.SUCCESS('Successfully updated the filters from Edurep'))
        except Exception as exc:
            raise CommandError(str(exc))
