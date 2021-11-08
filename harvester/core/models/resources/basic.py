from copy import copy
import boto3
from urlobject import URLObject
import logging
from json import JSONDecodeError

from datagrowth.resources import MicroServiceResource, URLResource
import extruct


s3_client = boto3.client("s3")
logger = logging.getLogger("harvester")


class HttpTikaResource(MicroServiceResource):

    MICRO_SERVICE = "analyzer"
    HEADERS = {
        "Content-Type": "application/json"
    }

    def has_video(self):
        tika_content_type, data = self.content
        if data is None:
            return False
        text = data.get("text", "")
        content_type = data.get("content-type", "")
        if "leraar24.nl/api/video/" in text:
            return True
        if "video" in content_type:
            return True
        return any("video" in key for key in data.keys())

    def is_zip(self):
        tika_content_type, data = self.content
        if data is None:
            return False
        content_type = data.get("mime-type", "")
        return content_type == "application/zip"

    @staticmethod
    def hash_from_data(data):
        if not data:
            return ""
        signed_url = URLObject(data["url"])
        signature_keys = [key for key in signed_url.query_dict.keys() if key.startswith("X-Amz")]
        unsigned_url = signed_url.del_query_params(signature_keys)
        unsigned_data = copy(data)
        unsigned_data["url"] = unsigned_url
        return MicroServiceResource.hash_from_data(unsigned_data)


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
