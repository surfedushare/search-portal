import os
from PIL import Image

from django.conf import settings
from django.core.files.storage import default_storage

from core.utils.resources import serialize_resource

THUMBNAIL_SIZES = [(400, 300), (200, 150)]


def store_previews(destination_location, document_id):
    with open(f"{settings.BASE_DIR}/screenshot-{document_id}.png", "rb") as file:
        default_storage.save(
            f"{destination_location}/preview.png",
            file
        )

    for (width, height) in THUMBNAIL_SIZES:
        with open(f"{settings.BASE_DIR}/screenshot-{document_id}-{width}x{height}.png", "rb") as file:
            default_storage.save(
                f"{destination_location}/preview-{width}x{height}.png",
                file
            )


def update_document(document, resource, preview_path):
    pipeline = document.properties.get("pipeline", {})
    pipeline.update({
        "preview": serialize_resource(resource)
    })
    document.properties.update({
        "preview_path": preview_path,
        "pipeline": pipeline
    })
    document.save()


def remove_files_from_filesystem(document_id):
    os.remove(f"{settings.BASE_DIR}/screenshot-{document_id}.png")

    for (width, height) in THUMBNAIL_SIZES:
        os.remove(f"{settings.BASE_DIR}/screenshot-{document_id}-{width}x{height}.png")


def create_thumbnails(screenshot_location, document_id):
    screenshot = Image.open(screenshot_location)

    for (width, height) in THUMBNAIL_SIZES:
        screenshot = Image.open(screenshot_location)
        screenshot.thumbnail((width, height), Image.ANTIALIAS)
        screenshot.save(f"{settings.BASE_DIR}/screenshot-{document_id}-{width}x{height}.png")
