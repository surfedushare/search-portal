import os
from invoke import task, Exit

from commands import HARVESTER_DIR
from commands.aws.ecs import run_data_engineering_task
from environments.data_engineering.configuration import create_configuration


def run_harvester_task(ctx, mode, command, environment=None):
    # On localhost we call the command directly and exit
    if ctx.config.service.env == "localhost":
        with ctx.cd(HARVESTER_DIR):
            ctx.run(" ".join(command), echo=True)
        return
    # For remotes we need to determine which target(s) we want to run commands for
    target_input = input("Which projects do you want to run this command for (e)dusources, (p)ublinova or (b)oth? ")
    targets = []
    match target_input:
        case "e":
            targets.append("edusources")
        case "p":
            targets.append("publinova")
        case "b":
            targets += ["edusources", "publinova"]
        case _:
            raise Exit("Aborted running harvester command, because of invalid target input", code=1)
    # On AWS we trigger a harvester task on the container cluster to run the command for us
    for target in targets:
        run_data_engineering_task(ctx, target, mode, command, environment)


@task(
    name="migrate",
    help={
        "mode": "Mode you want to migrate: development, acceptance or production. Must match APPLICATION_MODE"
    }
)
def harvester_migrate(ctx, mode):
    """
    Executes migration task on container cluster for development, acceptance or production environment on AWS
    """
    command = ["python", "manage.py", "migrate"]
    environment = [
        {
            "name": "POL_POSTGRES_USER",
            "value": f"{ctx.config.postgres.user}"
        },
        {
            "name": "POL_SECRETS_POSTGRES_PASSWORD",
            "value": f"{ctx.config.aws.postgres_password_arn}"
        },
    ]
    run_harvester_task(ctx, mode, command, environment)


@task(help={
    "mode": "Mode you want to load data for: localhost, development, acceptance or production. "
            "Must match APPLICATION_MODE",
    "source": "Source you want to import from: development, acceptance or production.",
    "dataset": "The name of the greek letter that represents the dataset you want to import",
    "download_edurep": "If edurep should be downloaded, defaults to False"
})
def load_data(ctx, mode, source, dataset, download_edurep=False):
    """
    Loads the production database and sets up Open Search data on localhost or an AWS cluster
    """
    if ctx.config.service.env == "production":
        raise Exit("Cowardly refusing to use production as a destination environment")

    command = ["python", "manage.py", "load_harvester_data", dataset, f"--harvest-source={source}", "--index"]

    if download_edurep:
        print("Will download edurep data, this can take a while...")
        command += ["--download-edurep"]

    if source == "localhost":
        print(f"Will try to import {dataset} using pre-downloaded files")
        command += ["--skip-download"]

    run_harvester_task(ctx, mode, command)


@task(help={
    "mode": "Mode you want to migrate: localhost, development, acceptance or production. Must match APPLICATION_MODE",
    "reset": "Whether to reset the active datasets before harvesting",
    "no_promote": "Whether you want to create new indices without adjusting latest aliases",
})
def harvest(ctx, mode, reset=False, no_promote=False):
    """
    Starts a harvest tasks on the AWS container cluster or localhost
    """
    command = ["python", "manage.py", "run_harvest"]
    if reset:
        command += ["--reset"]
    if no_promote:
        command += ["--no-promote"]

    run_harvester_task(ctx, mode, command)


@task(help={
    "mode": "Mode you want to generate previews for: localhost, development, acceptance or production. "
            "Must match APPLICATION_MODE",
    "dataset": "Name of the dataset (a Greek letter) that you want to generate previews for"
})
def generate_previews(ctx, mode, dataset):
    command = ["python", "manage.py", "generate_previews", f"--dataset={dataset}"]
    run_harvester_task(ctx, mode, command)


@task(name="sync_preview_media", help={
    "source": "The source you want to sync preview media from"
})
def sync_preview_media(ctx, source="production"):
    """
    Performs a sync between the preview media buckets of two environments.
    APPLICATION_MODE determines the destination environment.
    """
    if ctx.config.service.env == "production":
        raise Exit("Cowardly refusing to use production as a destination environment")

    local_directory = os.path.join("media", "harvester")
    source_config = create_configuration(source, context="host")
    source = source_config.aws.harvest_content_bucket
    source = "s3://" + source if source is not None else local_directory
    destination = ctx.config.aws.harvest_content_bucket
    destination = "s3://" + destination if destination is not None else local_directory
    profile_name = ctx.config.aws.profile_name if not ctx.config.service.env == "localhost" else \
        source_config.aws.profile_name
    for path in ["thumbnails", os.path.join("core", "previews")]:
        source_path = os.path.join(source, path)
        destination_path = os.path.join(destination, path)
        ctx.run(f"AWS_PROFILE={profile_name} aws s3 sync {source_path} {destination_path}", echo=True)


@task(help={
    "mode": "Mode you want to clean data for: localhost, development, acceptance or production. "
            "Must match APPLICATION_MODE"
})
def clean_data(ctx, mode):
    """
    Starts a clean up tasks on the AWS container cluster or localhost
    """
    command = ["python", "manage.py", "clean_data"]

    run_harvester_task(ctx, mode, command)


@task(help={
    "mode": "Mode you want to extend resource cache for: localhost, development, acceptance or production. "
            "Must match APPLICATION_MODE"
})
def extend_resource_cache(ctx, mode):
    """
    Extends the purge_at time for Resources on the AWS container cluster or localhost
    """
    command = ["python", "manage.py", "extend_resource_cache"]

    run_harvester_task(ctx, mode, command)


@task(help={
    "mode": "Mode you want to create indices for: localhost, development, acceptance or production. "
            "Must match APPLICATION_MODE",
    "dataset": "Name of the dataset (a Greek letter) that you want to create indices for",
    "version": "Version of the harvester that created the dataset version you want to index. "
               "Defaults to latest version",
})
def index_dataset_version(ctx, mode, dataset, version=None, skip_evaluation=False):
    """
    Starts a task on the AWS container cluster or localhost to create the ES indices for a DatasetVersion
    """
    command = ["python", "manage.py", "index_dataset_version", f"--dataset={dataset}"]
    if version:
        command += [f"--harvester-version={version}"]
    if skip_evaluation:
        command += ["--skip-evaluation"]
    run_harvester_task(ctx, mode, command)


@task(help={
    "mode": "Mode you want to push indices for: localhost, development, acceptance or production. "
            "Must match APPLICATION_MODE",
    "dataset": "Name of the dataset (a Greek letter) that you want to promote to latest index "
               "(ignored if version_id is specified)",
    "version": "Version of the harvester that created the dataset version you want to index "
               "Defaults to latest version (ignored if version_id is specified)",
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
    run_harvester_task(ctx, mode, command)


@task(help={
    "mode": "Mode you want to dump data for: localhost, development, acceptance or production. "
            "Must match APPLICATION_MODE",
    "dataset": "Name of the dataset (a Greek letter) that you want to dump"
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
    source_config = create_configuration(source, context="host")
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


@task(help={
    "mode": "Mode you want to sync metadata for: localhost, development, acceptance or production. "
            "Must match APPLICATION_MODE"
})
def sync_metadata(ctx, mode):
    command = ["python", "manage.py", "sync_metadata"]

    run_harvester_task(ctx, mode, command)
