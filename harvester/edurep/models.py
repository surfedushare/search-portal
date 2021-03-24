from urlobject import URLObject

from core.models import HarvestHttpResource


class EdurepOAIPMH(HarvestHttpResource):

    URI_TEMPLATE = "https://wszoeken.edurep.kennisnet.nl/edurep/oai?set={}&from={}"
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
