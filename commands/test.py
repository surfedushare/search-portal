from invoke.tasks import task
from invoke import Collection

from commands.deploy.container import prepare_builds


@task(prepare_builds)
def e2e(ctx):
    with ctx.cd("portal"):
        ctx.run("npm run build")
        ctx.run("npm run test:e2e")
    with ctx.cd("service"):
        ctx.run("python manage.py test e2e_tests --failfast", echo=True, pty=True)


@task
def service(ctx):
    with ctx.cd("service"):
        ctx.run("python manage.py compilemessages", echo=True, pty=True)
        ctx.run("python manage.py collectstatic --no-input", echo=True, pty=True)
        ctx.run("python manage.py test", echo=True, pty=True)


@task
def harvester(ctx):
    with ctx.cd("harvester"):
        ctx.run("python manage.py test", echo=True, pty=True)


@task
def run(ctx):
    tests = [service, harvester]
    if ctx.config.project.name == "edusources":
        tests.append(e2e)
    for test in tests:
        test(ctx)


test_collection = Collection(
    "test",
    e2e,
    service,
    harvester,
    run
)
