from collections import defaultdict
import requests

from django.conf import settings
from django.utils.functional import cached_property


class MetadataTree(object):

    harvester_url = None
    api_token = None

    def __init__(self, harvester_url, api_token, warm_up_cache=False):
        self.harvester_url = harvester_url
        self.api_token = api_token
        if warm_up_cache:
            self._warm_up_cache = self.translations  # result should be ignored as it only fills the cache

    def _fetch(self, url):
        response = requests.get(url, headers={"Authorization": f"Token {self.api_token}"})
        if response.status_code != requests.status_codes.codes.ok:
            raise ValueError(f"Failed request: {response.status_code}")
        return response.json()

    @cached_property
    def tree(self):
        return self._fetch(f"{self.harvester_url}metadata/tree/?site_id={settings.SITE_ID}")

    @cached_property
    def partial_tree(self):
        return self._fetch(f"{self.harvester_url}metadata/tree/?site_id={settings.SITE_ID}&max_children=20")

    @cached_property
    def cache(self):
        cache = defaultdict(dict)

        def _cache_children(field_name, children):
            for child in children:
                cache[field_name][child["value"]] = child
                _cache_children(field_name, child["children"])

        for field in self.tree:
            field_name = field["value"]
            cache[field_name]["_field"] = field
            _cache_children(field_name, field["children"])

        return cache

    @cached_property
    def translations(self):
        return {
            field["value"]: {
                value: child["translation"]
                for value, child in self.cache[field["value"]].items()
            }
            for field in self.tree
        }

    def get_field(self, field_name):
        return self.cache[field_name]["_field"]

    def get_filter_field_names(self):
        return [
            field["value"]
            for field in self.tree if not field["is_manual"]
        ]
