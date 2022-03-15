import logging

from django.db import models
from urlobject import URLObject

from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor

from core.models import HarvestHttpResource
from sources.extraction.han import HanDataExtraction, HAN_EXTRACTION_OBJECTIVE


logger = logging.getLogger("harvester")


class HanOAIPMHManager(models.Manager):

    def extract_seeds(self, set_specification, latest_update):
        queryset = self.get_queryset() \
            .filter(set_specification=set_specification, since__date__gte=latest_update.date(), status=200)

        oaipmh_objective = {
            "@": HanDataExtraction.get_oaipmh_records,
            "external_id": HanDataExtraction.get_oaipmh_external_id,
            "state": HanDataExtraction.get_oaipmh_record_state
        }
        oaipmh_objective.update(HAN_EXTRACTION_OBJECTIVE)
        extract_config = create_config("extract_processor", {
            "objective": oaipmh_objective
        })
        prc = ExtractProcessor(config=extract_config)

        results = []
        for harvest in queryset:
            seed_resource = {
                "resource": f"{harvest._meta.app_label}.{harvest._meta.model_name}",
                "id": harvest.id,
                "success": True
            }
            try:
                for seed in prc.extract_from_resource(harvest):
                    seed["seed_resource"] = seed_resource
                    results.append(seed)
            except ValueError as exc:
                logger.warning("Invalid XML:", exc, harvest.uri)
        return results


class HanOAIPMHResource(HarvestHttpResource):

    objects = HanOAIPMHManager()

    set_specification = models.CharField(max_length=255, blank=True, null=False)

    URI_TEMPLATE = "https://repository.han.nl/hanoai/request"
    PARAMETERS = {
        "verb": "ListRecords",
        "metadataPrefix": "nl_didl"
    }

    def next_parameters(self):
        content_type, soup = self.content
        resumption_token = soup.find("resumptiontoken")
        if not resumption_token or not resumption_token.text:
            return {}
        return {
            "verb": "ListRecords",
            "resumptionToken": resumption_token.text
        }

    def create_next_request(self):
        next_request = super().create_next_request()
        if not next_request:
            return
        url = URLObject(next_request.get("url"))
        url = url.without_query().set_query_params(**self.next_parameters())
        next_request["url"] = str(url)
        return next_request

    class Meta:
        verbose_name = "HAN OAIPMH harvest"
        verbose_name_plural = "HAN OAIPMH harvests"
