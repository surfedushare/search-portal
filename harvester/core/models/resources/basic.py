import logging
import os
import json
from urllib.parse import quote_plus
from copy import copy
import boto3
from botocore.exceptions import ClientError
from urlobject import URLObject

from django.conf import settings
from django.db import models
from datagrowth.resources import HttpFileResource, TikaResource as DGTikaResource, file_resource_delete_handler


logger = logging.getLogger("harvester")
s3_client = boto3.client("s3")


class FileResource(HttpFileResource):

    def get_signed_absolute_uri(self, duration=7200):
        """
        Generate a presigned URL to share the S3 object where this resource is stored.
        If the application is not connected to S3 it simply returns a local path.
        """
        if settings.AWS_STORAGE_BUCKET_NAME is None:
            return os.path.join(settings.MEDIA_URL, quote_plus(self.body, safe="/"))

        # Generate a presigned URL for the S3 object
        lookup_params = {
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": self.body
        }
        try:
            url = s3_client.generate_presigned_url("get_object", Params=lookup_params, ExpiresIn=duration)
            return url
        except ClientError as e:
            logger.error(e)
            return None


class TikaResource(DGTikaResource):

    CMD_TEMPLATE = [
        "java",
        "-jar",
        "tika-app-1.25.jar",
        "-J",
        "-t",
        "{}"
    ]

    def has_video(self):
        tika_content_type, data = self.content
        if data is None:
            return False
        text = data.get("X-TIKA:content", "")
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
        content_type = data.get("Content-Type", "")
        return content_type == "application/zip"

    @property
    def content(self):
        content_type, raw = super(DGTikaResource, self).content
        if not raw:
            return content_type, raw
        docs = json.loads(raw)
        data = docs[0]
        data["X-TIKA:content"] = "\n\n".join(
            [f"{doc.get('resourceName', '')}\n\n{doc['X-TIKA:content']}"
             for doc in docs if doc.get('X-TIKA:content', None)]
        )
        variables = self.variables()
        data["resourcePath"] = variables["input"][0]
        return content_type, data

    @staticmethod
    def uri_from_cmd(cmd):
        """
        Removes the AWS signature from the command to be able to lookup similar runs with different signatures
        """
        cmd = copy(cmd)
        signed_url = URLObject(cmd[-1])
        signature_keys = [key for key in signed_url.query_dict.keys() if key.startswith("X-Amz")]
        unsigned_url = signed_url.del_query_params(signature_keys)
        cmd[-1] = str(unsigned_url)
        return DGTikaResource.uri_from_cmd(cmd)


models.signals.post_delete.connect(
    file_resource_delete_handler,
    sender=FileResource,
    dispatch_uid="file_resource_delete"
)
