from django.core.management import call_command
from celery import current_app as app


@app.task(name="clean_data")
def clean_data():
    call_command("clean_data")


@app.task(name="promote_dataset_version")
def promote_dataset_version(dataset_version_id):
    call_command("promote_dataset_version", f"--dataset-version-id={dataset_version_id}")
