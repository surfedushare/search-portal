import json
from urlobject import URLObject

from django.conf import settings
from django.db import models

from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor

from core.models import HarvestHttpResource
from sharekit.extraction import SharekitMetadataExtraction, SHAREKIT_EXTRACTION_OBJECTIVE


class SharekitMetadataHarvestManager(models.Manager):

    def extract_seeds(self, set_specification, latest_update):
        queryset = self.get_queryset() \
            .filter(set_specification=set_specification, since__date__gte=latest_update.date(), status=200)

        oaipmh_objective = {
            "@": "$.data",
            "external_id": "$.id",
            "state": SharekitMetadataExtraction.get_record_state
        }
        oaipmh_objective.update(SHAREKIT_EXTRACTION_OBJECTIVE)
        extract_config = create_config("extract_processor", {
            "objective": oaipmh_objective
        })
        prc = ExtractProcessor(config=extract_config)

        results = []
        for harvest in queryset:
            results += list(prc.extract_from_resource(harvest))
        return results


class SharekitMetadataHarvest(HarvestHttpResource):

    objects = SharekitMetadataHarvestManager()

    URI_TEMPLATE = "https://api.surfsharekit.nl/api/jsonapi/channel/v1/{}/repoItems?filter[modified][GE]={}"
    PARAMETERS = {
        "page[size]": 10
    }

    def auth_headers(self):
        return {
            "Authorization": f"Bearer {settings.SHAREKIT_API_KEY}"
        }

    def next_parameters(self):
        content_type, data = self.content
        next_link = data["links"].get("next", None)
        if not next_link:
            return {}
        next_url = URLObject(next_link)
        return {
            "page[number]": next_url.query_dict["page[number]"]
        }

    class Meta:
        verbose_name = "Sharekit metadata harvest"
        verbose_name_plural = "Sharekit metadata harvest"
