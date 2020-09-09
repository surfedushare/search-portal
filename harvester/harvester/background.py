import logging

from django.core.management import call_command

from harvester.settings import environment
from harvester.celery import app
from core.models import Dataset, OAIPMHHarvest
from core.constants import HarvestStages
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
            # TODO: enable this line for "primary" once the NAT gateway on AWS passes on internet
            # call_command("harvest_edurep_seeds", f"--dataset={dataset.name}")
            # TODO: this command should only be run if role is not primary once everything is migrated to AWS
            call_command("load_edurep_oaipmh_data", "--force-download")
            # After getting all the metadata we'll download content
            call_command("harvest_basic_content", f"--dataset={dataset.name}")
            # We skip any video downloading/processing for now
            # Later we want YoutubeDL to download the videos and Amber to process them
            OAIPMHHarvest.objects.filter(stage=HarvestStages.BASIC).update(stage=HarvestStages.VIDEO)
            # Aggregating the metadata and content into the dataset
            call_command("update_dataset", f"--dataset={dataset.name}")
            # Based on the dataset we push to Elastic Search
            call_command("push_es_index", f"--dataset={dataset.name}")
