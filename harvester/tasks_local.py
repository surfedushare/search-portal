import os
from invoke import task


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
    "dataset": "The name of the greek letter that represents the dataset you want to import"
})
def import_dataset(ctx, dataset="epsilon"):
    """
    Sets up the database with some basic data for the harvester
    """
    with ctx.cd(HARVESTER_DIR):
        ctx.run(f"python manage.py load_harvester_data {dataset}")
