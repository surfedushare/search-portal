import os
import factory
from datetime import datetime
from urllib.parse import quote

from django.conf import settings
from django.utils.timezone import make_aware

from sources.models import HanOAIPMHResource


SLUG = "han"
ENDPOINT = HanOAIPMHResource.URI_TEMPLATE.replace("https//", "")
SET_SPECIFICATION = "col_20.500.12470_2"
METADATA_PREFIX = "nl_didl"
RESUMPTION_TOKEN = "MToxMDB8Mjp8Mzp8NDp8NTpubF9kaWRs"


class HanOAIPMHFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = HanOAIPMHResource
        strategy = factory.BUILD_STRATEGY

    class Params:
        is_initial = True
        number = 0
        resumption = None

    since = factory.Maybe(
        "is_initial",
        make_aware(datetime(year=1970, month=1, day=1)),
        make_aware(datetime(year=2020, month=2, day=10, hour=13, minute=8, second=39, microsecond=315000))
    )
    set_specification = SET_SPECIFICATION
    status = 200
    head = {
        "content-type": "application/xml"
    }

    @factory.lazy_attribute
    def uri(self):
        from_param = f"from={self.since:%Y-%m-%dT%H:%M:%SZ}"
        identity = quote(f"{from_param}&metadataPrefix={METADATA_PREFIX}&set={self.set_specification}", safe="=&") \
            if not self.resumption else f"resumptionToken={quote(self.resumption)}"
        return f"{ENDPOINT}?{identity}&verb=ListRecords"

    @factory.lazy_attribute
    def request(self):
        return {
            "args": [self.set_specification, f"{self.since:%Y-%m-%dT%H:%M:%SZ}"],
            "kwargs": {},
            "method": "get",
            "url": "https://" + self.uri,
            "headers": {},
            "data": {}
        }

    @factory.lazy_attribute
    def body(self):
        response_type = "initial" if self.is_initial else "delta"
        response_file = f"fixture.{SLUG}.{response_type}.{self.number}.xml"
        response_file_path = os.path.join(
            settings.BASE_DIR, "sources", "factories",
            SLUG,
            response_file
        )
        with open(response_file_path, "r") as response:
            return response.read()

    @classmethod
    def create_common_responses(cls, include_delta=False):
        cls.create(is_initial=True, number=0)
        cls.create(is_initial=True, number=1, resumption=RESUMPTION_TOKEN)
        if include_delta:
            cls.create(is_initial=False, number=0)
