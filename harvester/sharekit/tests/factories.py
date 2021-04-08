import factory
from datetime import datetime

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

    since = factory.Maybe(
        "is_initial",
        make_aware(datetime(year=1970, month=1, day=1)),
        make_aware(datetime(year=2020, month=2, day=10))
    )
    set_specification = "edusources"
    status = 200
    head = {
        "content-type": "json/application"
    }

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
