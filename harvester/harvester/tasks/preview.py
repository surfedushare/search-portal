import boto3
from PIL import Image
import os

from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings

from core.models import ChromeScreenshotResource, Document
from harvester.celery import app


THUMBNAIL_SIZES = [(400, 300), (200, 150)]


@app.task(
    name="generate_browser_preview",
    soft_time_limit=60,
    autoretry_for=(SoftTimeLimitExceeded,),
    default_retry_delay=10
)
def generate_browser_preview(document_id):
    document = Document.objects.get(pk=document_id)
    screenshot_location = f"{settings.BASE_DIR}/screenshot-{document_id}.png"
    resource = ChromeScreenshotResource()
    resource.run(document.properties["url"], screenshot=screenshot_location)

    if resource.success:
        bucket_folder_path = f"previews/{document.id}"
        create_thumbnails(screenshot_location, document.id)
        upload_preview_to_s3(bucket_folder_path, document.id)
        add_preview_path_to_document(document, bucket_folder_path)
        resource.close()
        remove_files_from_filesystem(document.id)


def upload_preview_to_s3(destination_location, document_id):
    if not settings.AWS_PREVIEWS_BUCKET_NAME:
        return

    s3_client = boto3.client('s3')
    s3_client.upload_file(
        f"{settings.BASE_DIR}/screenshot-{document_id}.png",
        settings.AWS_PREVIEWS_BUCKET_NAME,
        f"{destination_location}/preview.png"
    )

    for (width, height) in THUMBNAIL_SIZES:
        s3_client.upload_file(
            f"{settings.BASE_DIR}/screenshot-{document_id}-{width}x{height}.png",
            settings.AWS_PREVIEWS_BUCKET_NAME,
            f"{destination_location}/preview-{width}x{height}.png"
        )


def add_preview_path_to_document(document, preview_path):
    properties = document.properties
    properties["preview_path"] = preview_path
    document.properties = properties
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
