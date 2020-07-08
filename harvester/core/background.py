import logging

from django.core.management import call_command

from harvester.settings import environment
from harvester.celery import app


log = logging.getLogger(__file__)


@app.task(name="health_check")
def health_check():
    log.info(f"Healthy: {environment.django.domain}")


@app.task(name="import_dataset")
def celery_import_dataset(dataset):
    call_command("load_harvester_data", dataset, default_aws_credentials=True)
