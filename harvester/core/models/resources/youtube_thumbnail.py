import json
import os.path
from io import BytesIO
import requests
from requests.status_codes import codes
from urllib.parse import urlparse, urljoin
from urlobject import URLObject

from django.core.files import File
from django.db import models
from django.dispatch import receiver

from versatileimagefield.fields import VersatileImageField
from versatileimagefield.utils import build_versatileimagefield_url_set

from datagrowth.resources import ShellResource


class YoutubeThumbnailResource(ShellResource):

    preview = VersatileImageField(upload_to=os.path.join("core", "previews", "youtube"), null=True, blank=True)

    CMD_TEMPLATE = [
        "youtube-dl",
        "--sleep-interval", "2",
        "--max-sleep-interval", "5",
        "--skip-download",
        "--get-thumbnail",
        "{}"
    ]

    @staticmethod
    def get_preview_filename(thumbnail_url):
        # Normalize source urls
        if "vimeocdn" in thumbnail_url:
            vimeo_url = URLObject(thumbnail_url)
            thumbnail_url = vimeo_url.query_dict["src0"]
        url = urlparse(thumbnail_url)
        path = url.path
        remainder, filename = os.path.split(path)
        name, ext = os.path.splitext(filename)
        remainder, youtube_id = os.path.split(remainder)
        return f"{youtube_id}{ext}"

    def run(self, *args, **kwargs):
        resource = super().run(*args, **kwargs)
        thumbnail_url = resource.stdout.strip()
        if not thumbnail_url:
            resource.status = codes.gone
            resource.save()
            return resource
        response = requests.get(thumbnail_url)
        if response.status_code != requests.codes.ok:
            resource.status = response.status_code
            resource.save()
            return resource
        fp = BytesIO()
        fp.write(response.content)
        filename = self.get_preview_filename(thumbnail_url)
        resource.preview.save(filename, File(fp))
        return resource

    @property
    def success(self):
        return super().success and self.preview is not None

    @property
    def content(self):
        if self.success:
            signed_urls = build_versatileimagefield_url_set(self.preview, [
                ('full_size', 'url'),
                ('preview', 'thumbnail__400x300'),
                ('preview_small', 'thumbnail__200x150'),
            ])
            return "application/json", {
                image_key: urljoin(url, urlparse(url).path)
                for image_key, url in signed_urls.items()
            }
        return None, None

    def handle_errors(self):
        # Do not throw an error. We just have a material without a preview
        # when it is not possible to fetch the preview.
        return

    def get_extension(self):
        if self.stdout:
            metadata = json.loads(self.stdout)
            extension = os.path.splitext(metadata["thumbnail"])[1]
            return extension.split("?")[0]


@receiver(models.signals.post_delete, sender=YoutubeThumbnailResource)
def delete_youtube_thumbnail_images(sender, instance, **kwargs):
    if instance.preview:
        # Deletes images from VersatileImageField
        instance.preview.delete_all_created_images()
        # Deletes original image
        instance.preview.delete(save=False)
