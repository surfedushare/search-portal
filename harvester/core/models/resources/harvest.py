from dateutil.parser import parse as parse_date_string

from django.utils.timezone import make_aware, is_aware
from django.db import models
from datagrowth.resources import HttpResource


class HarvestHttpResource(HttpResource):

    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [
                {
                    "type": "string"
                },
                {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}(T\d{2}\:\d{2}\:\d{2}Z)?$"
                }
            ],
            "minItems": 1,
            "additionalItems": False
        }
    }

    set_specification = models.CharField(max_length=255, blank=True, null=False)
    use_multiple_sets = True
    since = models.DateTimeField()

    def variables(self, *args):
        vars = super().variables(*args)
        since_time = None
        if len(vars["url"]) == 2:
            since_time = vars["url"][1]
        elif len(vars["url"]) == 1:
            since_time = vars["url"][0]
        if isinstance(since_time, str):
            since_time = parse_date_string(since_time)
            if not is_aware(since_time):
                since_time = make_aware(since_time)
        vars["since"] = since_time
        return vars

    def clean(self):
        super().clean()
        variables = self.variables()
        if not self.set_specification and len(variables["url"]) == 2:
            self.set_specification = variables["url"][0]
        if not self.since:
            self.since = variables.get("since", None)

    def validate_request(self, request, validate_input=True):
        # Casting datetime to string, because we need strings to pass validation
        request["args"] = tuple([
            arg if isinstance(arg, str) else str(arg)
            for arg in request["args"]
        ])
        return super().validate_request(request, validate_input=validate_input)

    class Meta:
        abstract = True
