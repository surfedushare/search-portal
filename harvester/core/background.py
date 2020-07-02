import logging
from invoke import Context

from tasks_local import import_dataset
from harvester.settings import environment
from harvester.celery import app


log = logging.getLogger(__file__)


@app.task(name="health_check")
def health_check():
    log.info(f"Healthy: {environment.django.domain}")


@app.task(name="import_dataset")
def celery_import_dataset(dataset):
    ctx = Context(environment)
    import_dataset(ctx, dataset, use_aws_profile=False)
