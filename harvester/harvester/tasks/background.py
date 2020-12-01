import logging
from invoke import Context

from django.conf import settings
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

    # Iterate over all active datasets to get data updates
    for dataset in Dataset.objects.filter(is_active=True):
        # Sometimes we may want to trigger a complete dataset reset
        if reset and role == "primary":
            EdurepOAIPMH.objects.all().delete()
        if reset:
            dataset.reset()
        # First we call the commands that will query the OAI-PMH interfaces
        if role == "primary":
            call_command("harvest_edurep_seeds", f"--dataset={dataset.name}", "--no-progress")
        else:
            call_command("load_edurep_oaipmh_data", "--force-download", "--no-progress")
        # After getting all the metadata we'll download content
        call_command("harvest_basic_content", f"--dataset={dataset.name}", "--no-progress")
        # We skip any video downloading/processing for now
        # Later we want YoutubeDL to download the videos and Amber to process them
        OAIPMHHarvest.objects.filter(stage=HarvestStages.BASIC).update(stage=HarvestStages.VIDEO)
        # Aggregating the metadata and content into the dataset
        call_command("update_dataset", f"--dataset={dataset.name}", "--no-progress")
        # Based on the dataset we push to Elastic Search
        extra_push_index_args = ["--recreate"] if reset else []

        call_command("generate_browser_previews", f"--dataset={dataset.name}", "--no-progress")

        call_command("push_es_index", f"--dataset={dataset.name}", "--no-progress", *extra_push_index_args)

    # After processing all active datasets we dump the seeds and store on S3 so other nodes can use that
    if role == "primary":
        call_command("dump_resource", "edurep.EdurepOAIPMH")
        ctx = Context(environment)
        harvester_data_bucket = f"s3://{settings.AWS_STORAGE_BUCKET_NAME}/datasets/harvester/edurep"
        ctx.run(f"aws s3 sync {settings.DATAGROWTH_DATA_DIR}/edurep {harvester_data_bucket}", echo=True)
