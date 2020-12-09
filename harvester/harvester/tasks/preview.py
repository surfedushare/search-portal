from PIL import Image
import os

from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.core.files.storage import default_storage


from core.models import ChromeScreenshotResource, Document
from harvester.celery import app
from core.utils.resources import serialize_resource


THUMBNAIL_SIZES = [(400, 300), (200, 150)]


@app.task(
    name="generate_browser_preview",
    soft_time_limit=60,
    autoretry_for=(SoftTimeLimitExceeded,),
    default_retry_delay=10,
    max_retries=3
)
def generate_browser_preview(document_id):
    document = Document.objects.get(pk=document_id)
    screenshot_location = f"{settings.BASE_DIR}/screenshot-{document_id}.png"
    resource = ChromeScreenshotResource()
    resource.run(document.properties["url"], screenshot=screenshot_location)

    if resource.success:
        bucket_folder_path = f"previews/{document.id}"
        create_thumbnails(screenshot_location, document.id)
        store_previews(bucket_folder_path, document.id)
        update_document(document, resource, bucket_folder_path)
        resource.close()
        remove_files_from_filesystem(document.id)


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


def create_thumbnails(screenshot_location, document_id):
    screenshot = Image.open(screenshot_location)

    for (width, height) in THUMBNAIL_SIZES:
        resized = screenshot.resize((width, height), Image.ANTIALIAS)
        resized.save(f"{settings.BASE_DIR}/screenshot-{document_id}-{width}x{height}.png")


def remove_files_from_filesystem(document_id):
    os.remove(f"{settings.BASE_DIR}/screenshot-{document_id}.png")

    for (width, height) in THUMBNAIL_SIZES:
        os.remove(f"{settings.BASE_DIR}/screenshot-{document_id}-{width}x{height}.png")
