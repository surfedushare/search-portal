from celery.exceptions import SoftTimeLimitExceeded
import pdf2image

from django.conf import settings

from core.models import Document, FileResource
from core.utils.previews import store_previews, update_document, remove_files_from_filesystem, create_thumbnails
from core.logging import HarvestLogger
from harvester.celery import app


@app.task(
    name="generate_pdf_preview",
    soft_time_limit=60,
    autoretry_for=(SoftTimeLimitExceeded,),
    default_retry_delay=10,
    max_retries=3
)
def generate_pdf_preview(document_id, total):
    document = Document.objects.get(pk=document_id)
    file_resource = get_file_resource(document.properties)

    if file_resource:
        _, content = file_resource.content
        screenshot_location = f"{settings.BASE_DIR}/screenshot-{document_id}.png"
        convert_pdf_file_to_image(content, screenshot_location)
        bucket_folder_path = f"previews/{document.id}"
        create_thumbnails(screenshot_location, document.id)
        store_previews(bucket_folder_path, document.id)
        update_document(document, bucket_folder_path)
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


def convert_pdf_file_to_image(path_to_pdf, destination):
    image = pdf2image.convert_from_bytes(path_to_pdf.read(), single_file=True)[0]
    image.save(destination)


def get_file_resource(properties):
    file_resource_id = properties.get('pipeline', {}).get('file', {}).get('resource', [])[1]

    if file_resource_id:
        return FileResource.objects.get(id=file_resource_id)
