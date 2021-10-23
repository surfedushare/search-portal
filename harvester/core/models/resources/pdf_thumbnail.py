import os
from io import BytesIO
from urllib.parse import urlparse
from datetime import datetime

import pdf2image
from versatileimagefield.fields import VersatileImageField

from datagrowth.resources import HttpFileResource


class PdfThumbnailResource(HttpFileResource):

    preview = VersatileImageField(upload_to=os.path.join("core", "previews", "pdf"), null=True, blank=True)

    def _update_from_results(self, response):
        # Get the image file we want to save
        file = BytesIO(response.content)
        image = pdf2image.convert_from_bytes(file.read(), single_file=True, fmt="png")[0]
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
