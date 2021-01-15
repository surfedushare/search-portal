import os
import factory

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

    since = factory.Maybe("is_initial", "1970-01-01", "2020-02-10")
    set_specification = "surf"
    status = 200
    head = {
        "content-type": "text/xml"
    }

    @factory.lazy_attribute
    def uri(self):
        return "wszoeken.edurep.kennisnet.nl/edurep/oai?" \
               f"from={self.since}&metadataPrefix=lom&set={self.set_specification}&verb=ListRecords"

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
