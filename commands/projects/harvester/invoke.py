from invoke import task

from commands import HARVESTER_DIR
from commands.aws.ecs import run_task


@task(help={
    "mode": "Mode you want to migrate: localhost, development, acceptance or production. Must match APPLICATION_MODE",
    "dataset": "The name of the greek letter that represents the dataset you want to import"
})
def import_dataset(ctx, mode, dataset="epsilon"):
    """
    Loads the production database and sets up Elastic data on localhost or an AWS cluster
    """
    command = ["python", "manage.py", "import_dataset", dataset]
    # On localhost we call the command directly and exit
    if mode == "localhost":
        with ctx.cd(HARVESTER_DIR):
            ctx.run(" ".join(command))
        return
    # On AWS we trigger a harvester task on the container cluster to run the command for us
    run_task(ctx, "harvester", mode, command)


@task(help={
    "mode": "Mode you want to migrate: localhost, development, acceptance or production. Must match APPLICATION_MODE",
    "reset": "Whether to reset the active datasets before harvesting",
    "secondary": "Whether you want the node to replicate Edurep data or get it from Edurep directly"
})
def harvest(ctx, mode, reset=False, secondary=False):
    """
    Starts a harvest tasks on the AWS container cluster or localhost
    """
    command = ["python", "manage.py", "run_harvest"]
    if reset:
        command += ["--reset"]
    if secondary:
        command += ["--secondary"]
    # On localhost we call the command directly and exit
    if mode == "localhost":
        with ctx.cd(HARVESTER_DIR):
            ctx.run(" ".join(command))
        return
    # On AWS we trigger a harvester task on the container cluster to run the command for us
    run_task(ctx, "harvester", mode, command)


@task(help={
    "mode": "Mode you want to cleanup: localhost, development, acceptance or production. Must match APPLICATION_MODE"
})
def cleanup(ctx, mode):
    """
    Starts a clean up tasks on the AWS container cluster or localhost
    """
    command = ["python", "manage.py", "clean_resources"]
    # On localhost we call the command directly and exit
    if mode == "localhost":
        with ctx.cd(HARVESTER_DIR):
            ctx.run(" ".join(command))
        return
    # On AWS we trigger a harvester task on the container cluster to run the command for us
    run_task(ctx, "harvester", mode, command)
