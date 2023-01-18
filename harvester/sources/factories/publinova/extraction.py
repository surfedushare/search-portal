import os
import factory
from datetime import datetime

from django.conf import settings
from django.utils.timezone import make_aware

from sources.models import PublinovaMetadataResource


SLUG = "publinova"
ENDPOINT = PublinovaMetadataResource.URI_TEMPLATE.replace("https://", "")
SET_SPECIFICATION = "publinova"


class PublinovaMetadataResourceFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = PublinovaMetadataResource
        strategy = factory.BUILD_STRATEGY

    class Params:
        is_initial = True
        number = 0

    since = make_aware(datetime(year=1970, month=1, day=1))
    set_specification = SET_SPECIFICATION
    uri = ENDPOINT
    status = 200
    head = {
        "content-type": "application/json"
    }

    @factory.lazy_attribute
    def request(self):
        return {
            "args": [f"{self.since:%Y-%m-%dT%H:%M:%SZ}"],
            "kwargs": {},
            "method": "get",
            "url": "https://" + self.uri,
            "headers": {},
            "data": {}
        }

    @factory.lazy_attribute
    def body(self):
        response_type = "initial"
        response_file = f"fixture.{SLUG}.{response_type}.{self.number}.json"
        response_file_path = os.path.join(
            settings.BASE_DIR, "sources", "factories", "fixtures",
            response_file
        )
        with open(response_file_path, "r") as response:
            return response.read()

    @classmethod
    def create_common_responses(cls):
        cls.create(number=0)
        cls.create(number=1)
