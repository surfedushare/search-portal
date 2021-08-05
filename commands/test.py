import logging
from invoke.tasks import task
from invoke import Collection

from commands.deploy.container import prepare_builds


log = logging.getLogger(__file__)


@task(prepare_builds)
def prepare_e2e(ctx):
    with ctx.cd("portal"):
        ctx.run("npm run build")


@task(prepare_e2e)
def e2e(ctx):
    with ctx.cd("service"):
        ctx.run("APPLICATION_PROJECT=edusources python manage.py test e2e_tests", echo=True, pty=True)


@task
def service(ctx):
    with ctx.cd("service"):
        ctx.run("python manage.py test", echo=True, pty=True)


@task
def harvester(ctx):
    with ctx.cd("harvester"):
        ctx.run("python manage.py test", echo=True, pty=True)


@task(service, harvester, e2e)
def run(ctx):
    pass


test_collection = Collection(
    "test",
    e2e,
    service,
    harvester,
    run
)
