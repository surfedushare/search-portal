import os
import factory
from datetime import datetime
from urllib.parse import quote

from django.conf import settings
from django.utils.timezone import make_aware

from edurep.models import EdurepOAIPMH


class EdurepOAIPMHFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = EdurepOAIPMH
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
    set_specification = "surfsharekit"
    status = 200
    head = {
        "content-type": "text/xml"
    }

    @factory.lazy_attribute
    def uri(self):
        from_param = f"from={self.since:%Y-%m-%dT%H:%M:%SZ}"
        identity = quote(f"{from_param}&metadataPrefix=lom&set={self.set_specification}", safe="=&") \
            if not self.resumption else f"resumptionToken={quote(self.resumption)}"
        return f"staging.edurep.kennisnet.nl/edurep/oai?{identity}&verb=ListRecords"

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
        response_file = f"edurep-oaipmh.{response_type}.{self.number}.xml"
        response_file_path = os.path.join(settings.BASE_DIR, "edurep", "fixtures", response_file)
        with open(response_file_path, "r") as response:
            return response.read()

    @classmethod
    def create_common_edurep_responses(cls, include_delta=False):
        cls.create(is_initial=True, number=0)
        cls.create(is_initial=True, number=1, resumption="c1576069959151499|u|f1970-01-01T00:00:00Z|mlom|ssurf")
        if include_delta:
            cls.create(is_initial=False, number=0)
