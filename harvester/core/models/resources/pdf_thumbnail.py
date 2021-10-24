import os
from io import BytesIO
from urllib.parse import urlparse, urljoin
from datetime import datetime

import pdf2image
from pdf2image.exceptions import PDFPageCountError
from versatileimagefield.fields import VersatileImageField
from versatileimagefield.utils import build_versatileimagefield_url_set

from datagrowth.resources import HttpFileResource


class PdfThumbnailResource(HttpFileResource):

    preview = VersatileImageField(upload_to=os.path.join("core", "previews", "pdf"), null=True, blank=True)

    def _update_from_results(self, response):
        # Get the image file we want to save
        file = BytesIO(response.content)
        try:
            image = pdf2image.convert_from_bytes(file.read(), single_file=True, fmt="png")[0]
        except PDFPageCountError:
            self.status = 1
            return
        # Defer a file name from the URL
        path = urlparse(response.url).path
        tail, head = os.path.split(path)
        if not head:
            head = "index.png"
        name, extension = os.path.splitext(head)
        if not extension:
            extension = ".png"
        now = datetime.utcnow()
        file_name = self.get_file_name(f"{name}{extension}", now)
        # Save to instance
        self.preview.save(file_name, image.fp)

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
