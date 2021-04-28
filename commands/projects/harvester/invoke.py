import os
from invoke import task, Exit

from commands import HARVESTER_DIR
from commands.aws.ecs import run_task
from environments.surfpol.configuration import create_configuration


def run_harvester_task(ctx, mode, command, **kwargs):
    # On localhost we call the command directly and exit
    if ctx.config.env == "localhost":
        with ctx.cd(HARVESTER_DIR):
            ctx.run(" ".join(command), echo=True)
        return

    # On AWS we trigger a harvester task on the container cluster to run the command for us
    run_task(ctx, "harvester", mode, command, **kwargs)


@task(help={
    "source": "Source you want to import from: development, acceptance or production.",
    "dataset": "The name of the greek letter that represents the dataset you want to import"
})
def import_dataset(ctx, source, dataset):
    """
    Loads the production database and sets up Elastic data on localhost or an AWS cluster
    """

    command = ["python", "manage.py", "import_dataset", dataset, f"--harvest-source={source}"]

    if source == "localhost":
        print(f"Will try to import {dataset} using pre-downloaded files")
        command += ["--skip-download"]

    run_harvester_task(ctx, source, command)


@task(help={
    "mode": "Mode you want to migrate: localhost, development, acceptance or production. Must match APPLICATION_MODE",
    "reset": "Whether to reset the active datasets before harvesting",
    "secondary": "Whether you want the node to replicate Edurep data or get it from Edurep directly",
    "no_promote": "Whether you want to create new indices without adjusting latest aliases",
    "version": "Version of the harvester you want to harvest with. Defaults to latest version"
})
def harvest(ctx, mode, reset=False, secondary=False, no_promote=False, version=None):
    """
    Starts a harvest tasks on the AWS container cluster or localhost
    """
    command = ["python", "manage.py", "run_harvest"]
    if reset:
        command += ["--reset"]
    if secondary:
        command += ["--secondary"]
    if no_promote:
        command += ["--no-promote"]

    run_harvester_task(ctx, mode, command, version=version, extra_workers=reset, concurrency=8)


@task(help={
    "mode": "Mode you want to generate previews for: localhost, development, acceptance or production. "
            "Must match APPLICATION_MODE",
    "dataset": "Name of the dataset (a Greek letter) that you want to generate previews for",
    "version": "Version of the harvester you want to use. Defaults to latest version"
})
def generate_previews(ctx, mode, dataset, version=None):
    command = ["python", "manage.py", "generate_previews", f"--dataset={dataset}"]

    run_harvester_task(ctx, mode, command, version=version, extra_workers=True, concurrency=8)


@task(help={
    "mode": "Mode you want to cleanup: localhost, development, acceptance or production. Must match APPLICATION_MODE"
})
def cleanup(ctx, mode):
    """
    Starts a clean up tasks on the AWS container cluster or localhost
    """
    command = ["python", "manage.py", "clean_resources"]

    run_harvester_task(ctx, mode, command)


@task(help={
    "mode": "Mode you want to create indices for: localhost, development, acceptance or production. "
            "Must match APPLICATION_MODE",
    "dataset": "Name of the dataset (a Greek letter) that you want to create indices for",
    "version": "Version of the harvester you want to use. Defaults to latest version"
})
def index_dataset_version(ctx, mode, dataset, version=None):
    """
    Starts a task on the AWS container cluster or localhost to create the ES indices for a DatasetVersion
    """
    command = ["python", "manage.py", "index_dataset_version", f"--dataset={dataset}"]
    if version:
        command += [f"--harvester-version={version}"]
    run_harvester_task(ctx, mode, command, version=version)


@task(help={
    "mode": "Mode you want to push indices for: localhost, development, acceptance or production. "
            "Must match APPLICATION_MODE",
    "dataset": "Name of the dataset (a Greek letter) that you want to promote to latest index "
               "(ignored if version_id is specified)",
    "version": "Version of the harvester you want to use. Defaults to latest version "
               "(ignored if version_id is specified)",
    "version_id": "Id of the DatasetVersion you want to promote"
})
def promote_dataset_version(ctx, mode, dataset=None, version=None, version_id=None):
    """
    Starts a task on the AWS container cluster or localhost to promote a DatasetVersion index to latest
    """
    command = ["python", "manage.py", "promote_dataset_version", ]
    if version_id:
        command += [f"--dataset-version-id={version_id}"]
    elif dataset:
        command += [f"--dataset={dataset}"]
        if version:
            command += [f"--harvester-version={version}"]
    else:
        Exit("Either specify a dataset of a dataset version id")
    run_harvester_task(ctx, mode, command, version=version)


@task(help={
    "mode": "Mode you want to dump data for: localhost, development, acceptance or production. "
            "Must match APPLICATION_MODE",
    "dataset": "Name of the dataset (a Greek letter) that you want to dump",
})
def dump_data(ctx, mode, dataset):
    """
    Starts a task on the AWS container cluster to dump a specific Dataset and its related models
    """
    command = ["python", "manage.py", "dump_harvester_data", dataset]

    run_harvester_task(ctx, mode, command)


@task()
def sync_harvest_content(ctx, source, path="core"):
    """
    Performs a sync between the harvest content buckets of two environments
    """
    local_directory = os.path.join("media", "harvester")
    source_config = create_configuration(source, project="harvester", context="host")
    source = source_config.aws.harvest_content_bucket
    if source is None:
        source = local_directory
    else:
        source = "s3://" + source
    destination = ctx.config.aws.harvest_content_bucket
    if destination is None:
        destination = local_directory
    else:
        destination = "s3://" + destination
    source_path = os.path.join(source, path)
    destination_path = os.path.join(destination, path)
    ctx.run(f"aws s3 sync {source_path} {destination_path}", echo=True)
