from harvester.celery import app


@app.task(name="health_check")
def health_check():
    print("Healthy")
