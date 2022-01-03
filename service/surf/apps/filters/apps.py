from django.conf import settings
from django.apps import AppConfig
from django.core.cache import cache

from surf.apps.filters.metadata import MetadataTree


class FiltersConfig(AppConfig):

    name = 'surf.apps.filters'

    @property
    def metadata(self):
        cache_key = "filters.metadata"
        metadata = cache.get(cache_key, None)
        if metadata is not None:
            return metadata
        metadata = MetadataTree(
            harvester_url=settings.HARVESTER_API,
            api_token=settings.HARVESTER_API_KEY
        )
        cache.set(cache_key, metadata, 60*60)
        return metadata
