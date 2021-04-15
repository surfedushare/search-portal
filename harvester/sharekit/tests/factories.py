import os
import factory
from datetime import datetime

from django.conf import settings
from django.utils.timezone import make_aware

from sharekit.models import SharekitMetadataHarvest


class SharekitMetadataHarvestFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = SharekitMetadataHarvest
        strategy = factory.BUILD_STRATEGY

    class Params:
        set = "edusources"
        is_initial = True
        number = 0
        is_restricted = False

    since = factory.Maybe(
        "is_initial",
        make_aware(datetime(year=1970, month=1, day=1)),
        make_aware(datetime(year=2020, month=2, day=10))
    )
    set_specification = "edusources"
    status = 200
    head = {
        "content-type": "application/json"
    }

    @factory.lazy_attribute
    def set_specification(self):
        return "edusourcesprivate" if self.is_restricted else "edusources"

    @factory.lazy_attribute
    def uri(self):
        return f"api.surfsharekit.nl/api/jsonapi/channel/v1/{self.set_specification}/repoItems" \
               f"?modified={self.since.date()}"

    @factory.lazy_attribute
    def request(self):
        return {
            "args": [self.set_specification, self.since],
            "kwargs": {},
            "method": "get",
            "url": "https://" + self.uri,
            "headers": {}
        }

    @factory.lazy_attribute
    def body(self):
        response_type = "initial" if self.is_initial else "delta"
        response_file = f"sharekit-api.{response_type}.{self.number}.json"
        response_file_path = os.path.join(settings.BASE_DIR, "sharekit", "fixtures", response_file)
        with open(response_file_path, "r") as response:
            response_string = response.read()
            # We modify the reference to the own link to indicate the link has restricted materials if necessary
            if self.is_restricted:
                return response_string.replace("/edusources/", "/edusourcesprivate/")
            return response_string

    @classmethod
    def create_common_sharekit_responses(cls, include_delta=False, is_restricted=False):
        cls.create(is_initial=True, number=0, is_restricted=is_restricted)
        cls.create(is_initial=True, number=1, is_restricted=is_restricted)
        if include_delta:
            cls.create(is_initial=False, number=0, is_restricted=is_restricted)
