from datetime import date, timedelta, datetime
from urllib.parse import urlparse, parse_qs

from django.conf import settings
from django.db import models

from datagrowth.resources import HttpResource


class MatomoVisitsResourceManager(models.Manager):

    def iterate_visits(self, latest_update=None, include_staff=False, min_actions=None, filter_custom_events=None):
        if latest_update is None:
            latest_update = datetime.strptime(MatomoVisitsResource.DEFAULT_START_DATE, "%Y-%m-%d")
        queryset = self.get_queryset() \
            .filter(since__date__gte=latest_update.date(), status=200)
        for resource in queryset:
            content_type, data = resource.content
            for visit in data:
                if not include_staff and visit["dimension1"] == "true":
                    continue
                if min_actions and int(visit["actions"]) < min_actions:
                    continue
                if filter_custom_events:
                    custom_events = {
                        event_key: False
                        for event_key in filter_custom_events.keys()
                    }
                    for action in visit["actionDetails"]:
                        actual_category = action.get("eventCategory", None)
                        actual_action = action.get("eventAction", None)
                        event_key = f"{actual_category}.{actual_action}"
                        if event_key in filter_custom_events:
                            custom_events[event_key] = True
                    if custom_events != filter_custom_events:
                        continue
                yield visit


class MatomoVisitsResource(HttpResource):

    objects = MatomoVisitsResourceManager()

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
