import logging

from django.core.management import call_command

from harvester.settings import environment
from harvester.celery import app


log = logging.getLogger("harvester")


@app.task(name="health_check")
def health_check():
    log.info(f"Healthy: {environment.django.domain}")


@app.task(name="import_dataset")
def celery_import_dataset(dataset, role="primary"):
    skip_download = role != "primary"  # replica environments should not try to download data
    call_command("load_harvester_data", dataset, default_aws_credentials=True, skip_download=skip_download)
    call_command("push_es_index", dataset=dataset, recreate=True)
