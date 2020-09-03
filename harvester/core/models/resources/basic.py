import os

from django.conf import settings
from django.db import models
from datagrowth.resources import HttpFileResource, TikaResource as DGTikaResource, file_resource_delete_handler


class FileResource(HttpFileResource):

    def get_absolute_uri(self):
        return os.path.join(settings.MEDIA_URL, self.body)


class TikaResource(DGTikaResource):

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


models.signals.post_delete.connect(file_resource_delete_handler, sender=FileResource)
