import boto3
import logging
from json import JSONDecodeError

from datagrowth.resources import HttpResource, URLResource
import extruct


s3_client = boto3.client("s3")
logger = logging.getLogger("harvester")


class HttpTikaResource(HttpResource):

    URI_TEMPLATE = "http://localhost:9998/rmeta/text?fetchKey={}"
    PARAMETERS = {
        "fetcherName": "http"
    }

    def handle_errors(self):
        super().handle_errors()
        _, data = self.content
        has_content = False
        has_exception = False

        if (data):
            first_tika_result = data[0]
            has_content = first_tika_result["X-TIKA:content"] is not None and first_tika_result["X-TIKA:content"] != ""
            has_exception = len(
                dict(filter(lambda item:  "X-TIKA:EXCEPTION:" in item[0], first_tika_result.items()))) > 0

        if has_content and has_exception:
            self.status = 200
        elif not has_content and not has_exception:
            self.status = 204
        elif not has_content and has_exception:
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
