import logging
from invoke.tasks import task

from deploy import prepare_builds


log = logging.getLogger(__file__)


@task(prepare_builds)
def prepare_e2e_tests(ctx):
    with ctx.cd("portal"):
        ctx.run("npm run build -- --dest=../service/surf/apps/materials/static/portal/")


@task(prepare_e2e_tests)
def e2e_tests(ctx):
    with ctx.cd("service"):
        ctx.run(f"python manage.py test e2e_tests", echo=True, pty=True)


@task
def service_tests(ctx):
    with ctx.cd("service"):
        ctx.run(f"python manage.py test surf.apps", echo=True, pty=True)


@task
def elastic_search_tests(ctx):
    with ctx.cd("service"):
        ctx.run(f"python manage.py test surf.vendor", echo=True, pty=True)


@task
def harvester_tests(ctx):
    with ctx.cd("harvester"):
        ctx.run(f"python manage.py test", echo=True, pty=True)


@task(service_tests, harvester_tests, e2e_tests)
def test(ctx):
    pass
