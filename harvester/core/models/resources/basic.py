import boto3
import logging
from json import JSONDecodeError

from datagrowth.resources import HttpResource, URLResource
import extruct


s3_client = boto3.client("s3")
logger = logging.getLogger("harvester")


class HttpTikaResource(HttpResource):

    URI_TEMPLATE = "http://localhost:9090/rmeta/text?fetchKey={}"
    PARAMETERS = {
        "fetcherName": "http"
    }

    def handle_errors(self):
        super().handle_errors()
        _, data = self.content
        if (data):
            for key, value in data[0].items():
                if "X-TIKA:content" in key and (value is None or value == ""):
                    self.status = 1
                if "X-TIKA:EXCEPTION:" in key:
                    self.status = 1


class ExtructResource(URLResource):

    @property
    def success(self):
        success = super().success
        content_type, data = self.content
        return success and bool(data)

    @property
    def content(self):
        if super().success:
            content_type = self.head.get("content-type", "unknown/unknown").split(';')[0]
            if content_type != "text/html":
                return None, None
            try:
                result = extruct.extract(self.body)
                return "application/json", result
            except JSONDecodeError:
                pass
        return None, None
