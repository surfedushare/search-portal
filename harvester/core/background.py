import logging

from django.core.management import call_command

from harvester.settings import environment
from harvester.celery import app
from core.models import Dataset
from edurep.models import EdurepOAIPMH


log = logging.getLogger("harvester")


@app.task(name="health_check")
def health_check():
    log.info(f"Healthy: {environment.django.domain}")


@app.task(name="import_dataset")
def celery_import_dataset(dataset, role="primary"):
    call_command("load_harvester_data", dataset)
    call_command("push_es_index", dataset=dataset, recreate=True)


@app.task(name="harvest")
def harvest(role="primary", reset=False):
    # TODO: to limit resource use Edurep asked us to only sync with them once a day
    # We can facilitate this by loading the production OAI-PMH resources on development and acceptance.
    # We'll check the role and if it's not primary skip download.
    # However as we are developing I'm skipping this for now.

    # Iterate over all active datasets to get data updates
    for dataset in Dataset.objects.filter(is_active=True):
        # Sometimes we may want to trigger a complete dataset reset
        if reset and role == "primary":
            EdurepOAIPMH.objects.all().delete()
        if reset:
            dataset.reset()
        # First we call the commands that will query the OAI-PMH interfaces
        if role == "primary":
            call_command("harvest_edurep_seeds", f"--dataset={dataset}")
