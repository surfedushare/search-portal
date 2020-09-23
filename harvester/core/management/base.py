import os
import json
from urllib.parse import urlparse
from copy import copy
from tqdm import tqdm
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.utils.language import get_language_from_snippet


logger = logging.getLogger("harvester")


class HarvesterCommand(BaseCommand):
    """
    This class adds some syntax sugar to make output of all commands similar
    """

    show_progress = True
    use_logger = True

    def add_arguments(self, parser):
        parser.add_argument('-n', '--no-progress', action="store_true")
        parser.add_argument('-L', '--no-logger', action="store_false")

    def execute(self, *args, **options):
        self.show_progress = not options.get("no_progress", False)
        self.use_logger = options.get("no_logger", True)
        super().execute(*args, **options)

    def error(self, message):
        if self.use_logger:
            logger.error(message)
        self.stderr.write(self.style.ERROR(message))

    def warning(self, message):
        if self.use_logger:
            logger.warning(message)
        self.stderr.write(self.style.WARNING(message))

    def info(self, message, object=None, log=False):
        if self.use_logger:
            extra = {"extra": object} if object is not None else {}
            logger.info(message, extra=extra)
        if object is not None:
            message += " " + json.dumps(object, indent=4)
        self.stdout.write(message)

    def success(self, message):
        self.stdout.write(self.style.SUCCESS(message))

    def header(self, header, options=None):
        self.info("")
        self.info("")
        self.info(header)
        self.info("-" * len(header))
        if options:
            opts = copy(options)
            opts.pop("stdout", None)
            opts.pop("stderr", None)
            self.info("Options: ", opts)
        self.info("Commit: {}".format(settings.GIT_COMMIT))
        now = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        self.info("Time: {}".format(now))
        self.info("")

    def progress(self, iterator, total=None):
        if not self.show_progress:
            return iterator
        return tqdm(iterator, total=total)


class OutputCommand(HarvesterCommand):

    @staticmethod
    def _serialize_resource(resource=None):
        if resource is None:
            return {
                "success": False,
                "resource": None
            }
        return {
            "success": resource.success,
            "resource": ["{}.{}".format(resource._meta.app_label, resource._meta.model_name), resource.id]
        }

    def get_file_type(self, mime_type=None, url=None):
        # TODO: this part needs a big refactor
        file_type = None
        if mime_type:
            file_type = settings.MIME_TYPE_TO_FILE_TYPE.get(mime_type, None)
        if not file_type and url:
            url = urlparse(url)
            file, extension = os.path.splitext(url.path)
            if extension and extension.lower() not in settings.EXTENSION_TO_FILE_TYPE:
                self.warning("Unknown extension: {}".format(extension))
            file_type = settings.EXTENSION_TO_FILE_TYPE.get(extension.lower(), "unknown")
        return file_type

    def _create_document(self, text, meta, title=None, url=None, mime_type=None, file_type=None, pipeline=None,
                         identifier_postfix=None):

        url = url or meta.get("url")
        mime_type = mime_type or meta.get("mime_type", None)
        file_type = file_type or self.get_file_type(mime_type, url)

        identifier = meta["external_id"]
        if identifier_postfix:
            identifier += f":{identifier_postfix}"

        text_language = get_language_from_snippet(text)
        title = title or meta.get("title", None)
        title_language = get_language_from_snippet(title)
        meta_language = meta.get("language", None)

        pipeline = pipeline or {}
        assert isinstance(pipeline, dict), "Pipeline should be a dictionary got {} instead".format(type(pipeline))
        pipeline["harvest"] = settings.GIT_COMMIT

        return {
            "id": identifier,
            "external_id": meta["external_id"],
            "title": title,
            "language": {
                "metadata": meta_language,
                "from_text": text_language,
                "from_title": title_language
            },
            "url": url,
            "text": text,
            "file_type": file_type,
            "mime_type": mime_type,
            "author": meta.get("author", []),
            "authors": meta.get("authors", []),
            "publishers": meta.get("publishers", []),
            "description": meta.get("description", None),
            "copyright": meta.get("copyright", None),
            "aggregation_level": meta.get("aggregation_level", None),
            "publisher_date": meta.get("publisher_date", None),
            "disciplines": meta.get("disciplines", []),
            "educational_levels": meta.get("educational_levels", []),
            "lom_educational_levels": meta.get("lom_educational_levels", []),
            "lowest_educational_level": meta.get("lowest_educational_level", -1),
            "suggest": title,
            "pipeline": pipeline
        }
