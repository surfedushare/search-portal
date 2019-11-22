from django.db.models import Count
from django.core.management.base import BaseCommand

from surf.vendor.surfconext.models import DataGoalTypes
from surf.apps.users.models import User
from surf.apps.communities.models import Team


class Command(BaseCommand):

    def handle(self, *args, **options):
        # We'll find users that have communities assigned, but have not given permission to process communities
        users = User.objects \
            .annotate(num_communities=Count("community")) \
            .filter(
                num_communities__gt=0,
                datagoalpermission__is_allowed=False, datagoalpermission__goal__type=DataGoalTypes.COMMUNITIES
            )
        # Delete all teams for users that have not given permission
        Team.objects.filter(user__in=users).delete()
