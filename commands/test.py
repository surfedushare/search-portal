from invoke.tasks import task
from invoke import Collection

from commands.deploy.container import prepare_builds


@task(prepare_builds)
def e2e(ctx):
    with ctx.cd("portal"):
        ctx.run("npm run build")
    with ctx.cd("service"):
        ctx.run("APPLICATION_PROJECT=edusources python manage.py test e2e_tests --failfast", echo=True, pty=True)


@task
def service(ctx):
    with ctx.cd("service"):
        ctx.run("python manage.py compilemessages", echo=True, pty=True)
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
