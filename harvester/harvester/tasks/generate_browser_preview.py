from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings


from core.models import ChromeScreenshotResource, Document
from core.utils.previews import store_previews, update_document, remove_files_from_filesystem, create_thumbnails
from core.logging import HarvestLogger
from harvester.celery import app


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
        update_document(document, bucket_folder_path, resource)
        resource.close()
        remove_files_from_filesystem(document.id)

        logger = HarvestLogger(document.dataset.name, "generate_previews", {})
        logger.report_material(
            document.properties["external_id"],
            title=document.properties["title"],
            url=document.properties["url"],
            pipeline=document.properties["pipeline"],
            state="preview"
        )
