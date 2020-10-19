import os
import json
import hashlib
from datetime import datetime
from urlobject import URLObject

from django.conf import settings

from datagrowth.resources import ShellResource
from datagrowth import settings as datagrowth_settings


class YouTubeDLResource(ShellResource):

    CMD_TEMPLATE = [
        "youtube-dl",
        "--no-playlist",
        "--extract-audio",
        "--audio-format=wav",
        "--postprocessor-args=-ac 1 -ar 8000",
        "--print-json",
        "CMD_FLAGS",
        "{}"
    ]
    FLAGS = {
        "output": "--output="
    }

    def variables(self, *args):
        args = args or self.command.get("args")
        return {
            "url": args[0]
        }

    def run(self, *args, **kwargs):
        if "output" not in kwargs:
            vars = self.variables(*args)
            file_path, file_name, extension = self._get_file_info(vars["url"])
            kwargs["output"] = os.path.join(file_path, "%(id)s.%(ext)s")
        return super().run(*args, **kwargs)

    def transform(self, stdout):
        if not stdout:
            return {}
        metadata = json.loads(stdout)
        file_name = metadata.get("_filename", None)
        if not file_name:
            return {"metadata": metadata}
        name, ext = os.path.splitext(file_name)
        return {"file_path": f"{name}.wav", "metadata": metadata}

    def _get_file_info(self, url):
        # Getting the file name and extension from url
        path = str(URLObject(url).path)
        tail, head = os.path.split(path)
        name, extension = os.path.splitext(head)
        now = datetime.utcnow()
        file_name = "{}.{}".format(
            now.strftime(datagrowth_settings.DATAGROWTH_DATETIME_FORMAT),
            name
        )
        # Hashing the file name
        hasher = hashlib.md5()
        hasher.update(file_name.encode('utf-8'))
        file_hash = hasher.hexdigest()
        # Constructing file path
        file_path = os.path.join(
            settings.MEDIA_ROOT,
            self._meta.app_label,
            "downloads",
            file_hash[0], file_hash[1:3]  # this prevents huge (problematic) directory listings
        )
        return file_path, file_name, extension

    @staticmethod
    def uri_from_cmd(cmd):
        # We filter --output flag, because it's always unique for every invoke
        cmd = [part for part in cmd if not part.startswith("--output=")]
        return ShellResource.uri_from_cmd(cmd)

    def delete(self, using=None, keep_parents=False):
        if self.success:
            content_type, files = self.content
            for file in files:
                if os.path.exists(file):
                    os.remove(file)
        super().delete(using=using, keep_parents=keep_parents)
