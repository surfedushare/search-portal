import os
import factory
from datetime import datetime

from django.conf import settings
from django.utils.timezone import make_aware

from edurep.models import EdurepOAIPMH


class EdurepOAIPMHFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = EdurepOAIPMH
        strategy = factory.BUILD_STRATEGY

    class Params:
        set = "surf"
        is_initial = True
        number = 0

    since = factory.Maybe(
        "is_initial",
        make_aware(datetime(year=1970, month=1, day=1)),
        make_aware(datetime(year=2020, month=2, day=10))
    )
    set_specification = "surf"
    status = 200
    head = {
        "content-type": "text/xml"
    }

    @factory.lazy_attribute
    def uri(self):
        return "wszoeken.edurep.kennisnet.nl/edurep/oai?" \
               f"from={self.since.date()}&metadataPrefix=lom&set={self.set_specification}&verb=ListRecords"

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
        cls.create(is_initial=True, number=1)
        if include_delta:
            cls.create(is_initial=False, number=0)
