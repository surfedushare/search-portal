import os
from invoke import task

from commands.aws.ecs import run_task


HARVESTER_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HARVESTER_DIR, "..", "data", "harvester")


@task(name="setup", help={
    "skip_superuser": "Skip the createsuperuser command in case you already have one"
})
def setup_harvester(ctx, skip_superuser=False):
    """
    Sets up the database with some basic data for the harvester
    """
    with ctx.cd(HARVESTER_DIR):
        ctx.run("POL_DJANGO_POSTGRES_USER=postgres python manage.py migrate")
        if not skip_superuser:
            ctx.run("POL_DJANGO_POSTGRES_USER=postgres python manage.py createsuperuser", pty=True)
        ctx.run("python manage.py loaddata core/fixtures/datasets-history.json")
        ctx.run("python manage.py loaddata edurep/fixtures/surf-oaipmh-1970-01-01.json")


@task(help={
    "mode": "Mode you want to migrate: localhost, development, acceptance or production. Must match APPLICATION_MODE",
    "dataset": "The name of the greek letter that represents the dataset you want to import"
})
def import_dataset(ctx, mode, dataset="epsilon"):
    """
    Sets up the database with some basic data for the harvester
    """
    command = ["python", "manage.py", "import_dataset", dataset]
    # On localhost we call the command directly and exit
    if mode == "localhost":
        with ctx.cd(HARVESTER_DIR):
            ctx.run(" ".join(command))
        return
    # On AWS we trigger a harvester task on the container cluster to run the command for us
    run_task(ctx, "harvester", mode, command)
