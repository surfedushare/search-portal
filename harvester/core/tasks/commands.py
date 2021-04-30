from django.core.management import call_command
from celery import current_app as app


@app.task()
def clean_data():
    call_command("clean_data")
