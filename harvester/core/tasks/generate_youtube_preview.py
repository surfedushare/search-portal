from PIL import Image
import os.path

from celery.exceptions import SoftTimeLimitExceeded
from celery import current_app as app

from core.models import YoutubeThumbnailResource, Document
from core.utils.previews import store_previews, update_document, remove_files_from_filesystem, create_thumbnails
from core.logging import HarvestLogger


@app.task(
    name="generate_youtube_preview",
    soft_time_limit=60,
    autoretry_for=(SoftTimeLimitExceeded,),
    throws=(SoftTimeLimitExceeded,),
    default_retry_delay=10,
    max_retries=3
)
def generate_youtube_preview(document_id, total):
    document = Document.objects.get(pk=document_id)
    screenshot_location = f"screenshot-{document_id}"

    resource = YoutubeThumbnailResource()
    resource.run(document.properties["url"], output=screenshot_location)

    if resource.success:
        bucket_folder_path = f"previews/{document.id}"
        extension = resource.get_extension()
        full_filename = f"{screenshot_location}{extension}"
        convert_to_png(screenshot_location, extension)
        create_thumbnails(full_filename, document.id)
        store_previews(bucket_folder_path, document.id)
        update_document(document, bucket_folder_path, resource)
        resource.close()
        os.remove(full_filename)
        remove_files_from_filesystem(document.id)

        logger = HarvestLogger(document.dataset.name, "generate_previews", {})
        logger.progress("preview.generate", total)
        logger.report_material(
            document.properties["external_id"],
            title=document.properties["title"],
            url=document.properties["url"],
            pipeline=document.properties["pipeline"],
            state="preview"
        )


def convert_to_png(screenshot_location, extension):
    full_filename = f"{screenshot_location}{extension}"
    im = Image.open(full_filename).convert("RGB")
    im.save(f"{screenshot_location}.png", "png")
