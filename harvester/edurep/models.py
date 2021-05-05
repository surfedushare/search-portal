import logging
from urlobject import URLObject

from django.conf import settings
from django.db import models

from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor

from core.models import HarvestHttpResource
from edurep.extraction import EdurepDataExtraction, EDUREP_EXTRACTION_OBJECTIVE


logger = logging.getLogger("harvester")


class EdurepOAIPMHManager(models.Manager):

    def extract_seeds(self, set_specification, latest_update):
        queryset = self.get_queryset() \
            .filter(set_specification=set_specification, since__date__gte=latest_update.date(), status=200)

        oaipmh_objective = {
            "@": EdurepDataExtraction.get_oaipmh_records,
            "external_id": EdurepDataExtraction.get_oaipmh_external_id,
            "state": EdurepDataExtraction.get_oaipmh_record_state
        }
        oaipmh_objective.update(EDUREP_EXTRACTION_OBJECTIVE)
        extract_config = create_config("extract_processor", {
            "objective": oaipmh_objective
        })
        prc = ExtractProcessor(config=extract_config)

        results = []
        for harvest in queryset:
            try:
                results += list(prc.extract_from_resource(harvest))
            except ValueError as exc:
                logger.warning("Invalid XML:", exc, harvest.uri)
        return results


class EdurepOAIPMH(HarvestHttpResource):

    objects = EdurepOAIPMHManager()

    URI_TEMPLATE = settings.EDUREP_BASE_URL + "/edurep/oai?set={}&from={}"
    PARAMETERS = {
        "verb": "ListRecords",
        "metadataPrefix": "lom"
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

    def handle_errors(self):
        content_type, soup = self.content
        # If there is no response at all we indicate a service not available
        # Note that the IP might be blocked by Edurep
        if soup is None:
            self.status = 503
            super().handle_errors()
            return
        # Edurep always responds with a 200, but it may contain an error tag
        # If not we're fine and done handling errors
        error = soup.find("error")
        if error is None:
            return
        # If an error was found we translate it into an appropriate code
        status = error["code"]
        if status == "badArgument":
            self.status = 400
        elif status == "noRecordsMatch":
            self.status = 204
        # And we raise proper exceptions for the system to pick up
        super().handle_errors()

    class Meta:
        verbose_name = "Edurep OAIPMH harvest"
        verbose_name_plural = "Edurep OAIPMH harvests"
