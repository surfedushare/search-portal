from django.apps import apps
from django.utils.timezone import now

from core.management.base import HarvesterCommand


class Command(HarvesterCommand):
    """
    A convenience command to delete any resources that are erroneous or considered stale
    """

    resources = {
        "edurep.EdurepOAIPMH": 204,
        "core.FileResource": 300,
        "core.TikaResource": 1
    }

    def handle(self, **options):
        for resource_model, status_code_cutoff in self.resources.items():
            model = apps.get_model(resource_model)
            model.objects.filter(status__gte=status_code_cutoff).delete()
            model.objects.filter(purge_at__lte=now()).delete()
