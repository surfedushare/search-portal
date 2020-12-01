import boto3

from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings

from core.models import ChromeScreenshotResource, Document
from harvester.celery import app


@app.task(
    name="generate_browser_preview",
    soft_time_limit=30,
    autoretry_for=(SoftTimeLimitExceeded,),
    default_retry_delay=10
)
def generate_browser_preview(document_id):
    document = Document.objects.get(pk=document_id)
    screenshot_location = f"{settings.BASE_DIR}/screenshot-{document_id}.png"
    resource = ChromeScreenshotResource()
    resource.run(document.properties["url"], screenshot=screenshot_location)

    if resource.success:
        bucket_path = f"previews/{document.id}/preview.png"
        upload_preview_to_s3(screenshot_location, bucket_path)
        add_preview_to_document(document, bucket_path)
        resource.close()


def upload_preview_to_s3(source_location, destination_location):
    if not settings.AWS_PREVIEWS_BUCKET_NAME:
        return

    s3_client = boto3.client('s3')
    s3_client.upload_file(
        source_location,
        settings.AWS_PREVIEWS_BUCKET_NAME,
        destination_location
    )


def add_preview_to_document(document, preview_path):
    properties = document.properties
    properties["preview_path"] = preview_path
    document.properties = properties
    document.save()
