from copy import copy
import boto3
from urlobject import URLObject
import logging
from json import JSONDecodeError

from datagrowth.resources import HttpResource, URLResource
import extruct


s3_client = boto3.client("s3")
logger = logging.getLogger("harvester")


class HttpTikaResource(HttpResource):

    URI_TEMPLATE= "http://localhost:9090/rmeta/text?fetchKey={}"
    PARAMETERS = {
        "fetcherName": "http"
    }

    def handle_errors(self):
        pass
        content_type,data=self.content
        if "X-TIKA:EXCEPTION:embedded_exception" in data[0]:
            self.status=1

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
