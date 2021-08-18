import logging

from django.db import models
from urlobject import URLObject

from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor

from core.models import HarvestHttpResource
from anatomy_tool.extraction import AnatomyToolExtraction, ANATOMY_TOOL_EXTRACTION_OBJECTIVE


logger = logging.getLogger("harvester")


class AnatomyToolOAIPMHManager(models.Manager):

    def extract_seeds(self, set_specification, latest_update):
        queryset = self.get_queryset() \
            .filter(set_specification=set_specification, since__date__gte=latest_update.date(), status=200)

        oaipmh_objective = {
            "@": AnatomyToolExtraction.get_oaipmh_records,
            "external_id": AnatomyToolExtraction.get_oaipmh_external_id,
            "state": AnatomyToolExtraction.get_oaipmh_record_state
        }
        oaipmh_objective.update(ANATOMY_TOOL_EXTRACTION_OBJECTIVE)
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


class AnatomyToolOAIPMH(HarvestHttpResource):

    objects = AnatomyToolOAIPMHManager()

    URI_TEMPLATE = "https://anatomytool.org/oai-pmh?from={}"
    PARAMETERS = {
        "verb": "ListRecords",
        "metadataPrefix": "oai_lom"
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
        verbose_name = "Anatomy tool OAIPMH harvest"
        verbose_name_plural = "Anatomy tool OAIPMH harvests"
