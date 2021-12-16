import os
import factory
from datetime import datetime
from urllib.parse import quote
import json

from django.conf import settings
from django.utils.timezone import make_aware

from core.models import MatomoVisitsResource


class MatomoVisitsResourceFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = MatomoVisitsResource
        strategy = factory.BUILD_STRATEGY

    class Params:
        is_initial = True
        is_empty = False

    since = factory.Maybe(
        "is_initial",
        make_aware(datetime(year=2020, month=1, day=1)),
        make_aware(datetime(year=2020, month=2, day=10, hour=13, minute=8, second=39, microsecond=315000))
    )
    status = 200
    head = {
        "content-type": "application/json"
    }

    @factory.lazy_attribute
    def uri(self):
        return f"webstats.surf.nl/?date={self.since:%Y-%m-%dT%H:%M:%SZ}%2C2021-12-12&" \
               f"filter_offset=0&format=JSON&idSite=63&method=Live.getLastVisitsDetails&module=API&period=range"

    @factory.lazy_attribute
    def request(self):
        return {
            "args": [f"{self.since:%Y-%m-%d}"] if not self.is_initial else [],
            "kwargs": {},
            "method": "get",
            "url": "https://" + self.uri,
            "headers": {},
            "data": {}
        }

    @factory.lazy_attribute
    def body(self):
        if self.is_empty:
            return json.dumps([])
        response_file_path = os.path.join(
            settings.BASE_DIR,
            "core",
            "fixtures",
            "matomo-visits.json"
        )
        with open(response_file_path, "r") as response:
            return response.read()
