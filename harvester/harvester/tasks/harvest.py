from core.constants import HarvestStages, Repositories
from core.logging import HarvestLogger
from core.models import Dataset, Harvest
from core.utils.harvest import prepare_harvest
from django.conf import settings
from django.core.management import CommandError, call_command
from harvester.celery import app
from harvester.settings import environment
from invoke import Context


@app.task(name="harvest")
def harvest(reset=False, no_promote=False):

    if reset:
        call_command("extend_resource_cache")

    # Iterate over all active datasets to get data updates
    for dataset in Dataset.objects.filter(is_active=True):
        # Preparing dataset state and deletes old model instances
        prepare_harvest(dataset, reset=reset)
        # First we call the commands that will query the repository interfaces
        repositories = [
            Repositories.EDUREP, Repositories.SHAREKIT, Repositories.ANATOMY_TOOL,
            Repositories.HANZE, Repositories.HAN, Repositories.HKU, Repositories.GREENI
        ]
        for repository in repositories:
            try:
                call_command("harvest_metadata", f"--dataset={dataset.name}", f"--repository={repository}")
            except CommandError as exc:
                logger = HarvestLogger(dataset, "harvest_metadata", {
                    "dataset": dataset.name,
                    "repository": repository
                })
                logger.error(str(exc))

        # After getting all the metadata we'll download content
        call_command("harvest_basic_content", f"--dataset={dataset.name}", "--async")
        # We skip any video downloading/processing for now
        # Later we want YoutubeDL to download the videos and Amber to process them
        # Thumbnails are only enabled for Edusources not NPPO
        if settings.PROJECT == "edusources":
            Harvest.objects.filter(stage=HarvestStages.BASIC).update(stage=HarvestStages.PREVIEW)
            call_command("generate_previews", f"--dataset={dataset.name}", "--async")
        else:
            Harvest.objects.filter(stage=HarvestStages.BASIC).update(stage=HarvestStages.COMPLETE)
        # Based on the dataset we push to Elastic Search
        index_command = ["index_dataset_version", f"--dataset={dataset.name}"]
        if no_promote or not dataset.is_latest:
            index_command += ["--no-promote"]
        call_command(*index_command)

    # When dealing with a harvest on AWS seeds need to get copied to S3.
    # Localhost can use these copies instead of getting the seeds from behind Edurep's firewall.
    if settings.AWS_STORAGE_BUCKET_NAME:
        call_command("dump_resource", "edurep.EdurepOAIPMH")
        ctx = Context(environment)
        harvester_data_bucket = f"s3://{settings.AWS_STORAGE_BUCKET_NAME}/datasets/harvester/edurep"
        ctx.run(f"aws s3 sync --no-progress {settings.DATAGROWTH_DATA_DIR}/edurep {harvester_data_bucket}", echo=True)
