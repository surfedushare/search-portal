import json
import os.path

from datagrowth.resources import ShellResource


class YoutubeThumbnailResource(ShellResource):

    CMD_TEMPLATE = [
        "youtube-dl",
        "--write-thumbnail",
        "--skip-download",
        "--print-json",
        "--playlist-items=1",
        "CMD_FLAGS",
        "{}"
    ]

    FLAGS = {
        "output": "--output="
    }

    def handle_errors(self):
        # Do not throw an error. We just have a material without a preview
        # when it is not possible to fetch the preview.
        return

    def get_extension(self):
        if (self.stdout):
            metadata = json.loads(self.stdout)
            extension = os.path.splitext(metadata["thumbnail"])[1]
            return extension.split("?")[0]
