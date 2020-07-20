import os
from invoke import task


SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))


@task(name="setup", help={
    "skip_superuser": "Skip the createsuperuser command in case you already have one"
})
def setup_service(ctx, skip_superuser=False):
    """
    Sets up the (local) database for service backend
    """
    with ctx.cd(SERVICE_DIR):
        ctx.run("POL_DJANGO_POSTGRES_USER=postgres python manage.py migrate")
        if not skip_superuser:
            ctx.run("POL_DJANGO_POSTGRES_USER=postgres python manage.py createsuperuser", pty=True)
