import os
from glob import glob
from invoke import task


HARVESTER_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HARVESTER_DIR, "..", "data", "harvester")


@task(name="setup")
def setup_harvester(ctx):
    with ctx.cd(HARVESTER_DIR):
        ctx.run("POL_DJANGO_POSTGRES_USER=postgres python manage.py migrate")
        ctx.run("python manage.py createsuperuser")


@task()
def import_dataset(ctx, dataset):
    dumps_path = os.path.join(DATA_DIR, "core", "dumps", "dataset")
    dump_files = glob(os.path.join(dumps_path, f"{dataset}*"))
    if not len(dump_files):
        print(f"Downloading dump file for: {dataset}")
        ctx.run(f"AWS_DEFAULT_PROFILE=pol-dev aws s3 sync s3://edushare-data/datasets/harvester {DATA_DIR}")
    print(f"Importing dataset: {dataset}")
    with ctx.cd(HARVESTER_DIR):
        ctx.run(f"python manage.py load_harvester_data {dataset}")
