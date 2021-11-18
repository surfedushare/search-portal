from datetime import date, timedelta
from urllib.parse import urlparse, parse_qs

from django.conf import settings
from django.db import models

from datagrowth.resources import HttpResource


class MatomoVisitsResource(HttpResource):

    URI_TEMPLATE = "https://webstats.surf.nl/?date={}"
    PARAMETERS = {
        "module": "API",
        "method": "Live.getLastVisitsDetails",
        "format": "JSON",
        "period": "range",
        "filter_offset": "0",
        "idSite": "64"
    }
    DEFAULT_START_DATE = "2020-01-01"

    since = models.DateTimeField()

    def auth_parameters(self):
        return {
            "token_auth": settings.MATOMO_API_KEY
        }

    def next_parameters(self):
        content_type, data = self.content
        if not data:
            return {}
        url = urlparse(self.request["url"])
        params = parse_qs(url.query)
        offset = int(params["filter_offset"][0])
        return {
            "filter_offset": offset + 1
        }

    def _create_request(self, method, *args, **kwargs):
        start_date = kwargs.get("since", self.DEFAULT_START_DATE)
        end_date = date.today() - timedelta(days=1)
        date_range = f"{start_date},{end_date}"
        request = super()._create_request(method, date_range, **{})
        request["kwargs"] = kwargs
        return request

    def clean(self):
        super().clean()
        if not self.since and self.request:
            self.since = self.request["kwargs"].get("since", self.DEFAULT_START_DATE)
