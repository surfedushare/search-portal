from urlobject import URLObject
from dateutil.parser import parse as parse_date_string

from django.utils.timezone import make_aware
from django.db import models
from datagrowth.resources import HttpResource


class AnatomyToolOAIPMH(HttpResource):  # TODO: refactor with EdurepOAIPMH

    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [
                {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}(T\d{2}\:\d{2}\:\d{2}Z)?$"
                }
            ],
            "additionalItems": False
        }
    }

    since = models.DateTimeField()

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

    def variables(self, *args):
        vars = super().variables(*args)
        since_time = None
        if len(vars["url"]) >= 1:
            since_time = vars["url"][0]
            if isinstance(since_time, str):
                since_time = parse_date_string(since_time)
        vars["since"] = make_aware(since_time)
        return vars

    def clean(self):
        super().clean()
        variables = self.variables()
        if not self.since:
            self.since = variables.get("since", None)

    def send(self, method, *args, **kwargs):
        # We're sending along a default "from" parameter in a distant past to get all materials
        # if a set has been specified, but no start date.
        if len(args) == 0:
            args = ("1970-01-01",)
        return super().send(method, *args, **kwargs)

    def validate_request(self, request, validate_input=True):
        # Casting datetime to string, because we need strings to pass validation
        request["args"] = (str(request["args"][0]),)
        return super().validate_request(request, validate_input=validate_input)

    class Meta:
        verbose_name = "Anatomy tool OAIPMH harvest"
        verbose_name_plural = "Anatomy tool OAIPMH harvests"
