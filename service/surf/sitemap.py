from urllib.parse import quote
import requests

from dateutil.parser import isoparse

from django.conf import settings
from django.utils.functional import cached_property
from django.contrib.sitemaps import Sitemap


class MainSitemap(Sitemap):

    limit = 500
    changefreq = "monthly"
    protocol = "https"
    i18n = True
    languages = ["nl", "en"]
    alternates = True
    x_default = True

    def _location(self, item, force_lang_code=None):
        obj, lang_code = item
        return obj[force_lang_code] if force_lang_code else obj[lang_code]

    def items(self):
        return [
            {"nl": "/", "en": "/en"},
            {"nl": "/hoe-werkt-het", "en": "/en/how-does-it-work"}
        ]


class RemoteMaterialsList(object):

    url = None
    api_token = None

    def _get_response_data(self, url):
        response = requests.get(url, headers={"Authorization": f"Token {self.api_token}"})
        if response.status_code != requests.status_codes.codes.ok:
            print(response.content)
            raise ValueError("Failed request")
        return response.json()

    def __init__(self, url, api_token, page_size, page_parameter):
        self.url = url
        self.api_token = api_token
        self.page_size = page_size
        self.page_parameter = page_parameter

    @cached_property
    def _count(self):
        data = self._get_response_data(self.url)
        return data["count"]

    def __len__(self):
        return self._count

    def __getitem__(self, item):
        start, stop, step = item.indices(len(self))
        if step is not None and step != 1:
            raise ValueError(f"Unexpected step size for RemoteMaterialsList: {step}")
        if start % self.page_size:
            raise ValueError(f"Start should be a multiple of page_size {self.page_size}")
        page = int(start / self.page_size)
        last_page = self._count - page * self.page_size <= self.page_size
        if stop % self.page_size and not last_page:
            raise ValueError(f"End should be a multiple of page_size {self.page_size}")
        url = f"{self.url}?{self.page_parameter}={page}" if page else self.url
        data = self._get_response_data(url)
        return data["results"]


class MaterialsSitemap(Sitemap):

    limit = 500
    changefreq = "daily"
    protocol = "https"

    def location(self, obj):
        prefix = "materialen/" if obj["language"] == "nl" else "en/materials/"
        encoded_id = quote(
            obj['reference'],
            safe=";,:@&+$-_.!~*'()#"  # encodeURI minus /, = and & (vue-router "pretty" mode)
        )
        return f"/{prefix}{encoded_id}"

    def lastmod(self, obj):
        if obj["created_at"][:-7] == obj["modified_at"][:-7]:
            return
        return isoparse(obj["modified_at"])

    def items(self):
        return RemoteMaterialsList(
            url=f"{settings.HARVESTER_API}dataset/metadata-documents/",
            api_token=settings.HARVESTER_API_KEY,
            page_size=self.limit,
            page_parameter="page"
        )
