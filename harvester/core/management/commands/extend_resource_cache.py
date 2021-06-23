import logging

from django.apps import apps
from django.core.management.base import BaseCommand


logger = logging.getLogger("harvester")


class Command(BaseCommand):
    """
    A convenience command to extend validity of Resources
    """

    resources = [
        "core.FileResource",
        "core.HttpTikaResource",
    ]

    def handle(self, **options):
        for resource_model in self.resources:
            logger.info(f"Extending cache for: {resource_model}")
            model = apps.get_model(resource_model)
            instance = model()
            instance.clean()  # this calculates the preferred purge_at datetime
            model.objects.update(purge_at=instance.purge_at)
        logger.info("Done extending resource cache")
