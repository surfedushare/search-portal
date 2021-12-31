from django.conf import settings
from django.apps import AppConfig

from surf.apps.filters.metadata import MetadataTree


class FiltersConfig(AppConfig):

    name = 'surf.apps.filters'
    metadata = MetadataTree(
        harvester_url=settings.HARVESTER_API,
        api_token=settings.HARVESTER_API_KEY
    )
