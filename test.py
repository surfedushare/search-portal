import logging
from invoke.tasks import task

from deploy import prepare_builds


TEST_TARGETS = ["service~surf.apps", "service~surf.vendor", "harvester"]


log = logging.getLogger(__file__)


@task(prepare_builds)
def prepare_tests(ctx):
    with ctx.cd("portal"):
        ctx.run("npm run build -- --dest=../service/surf/apps/materials/static/portal/")


@task(prepare_tests, iterable=["target"])
def test(ctx, target):
    targets = target or TEST_TARGETS
    for target in targets:
        if target not in TEST_TARGETS:
            log.warning(f"Found invalid test target: {target}")
            continue
        log.info(f"Testing: {target}")
        target_info = target.split("~")
        if len(target_info) > 1:
            main, sub = target_info
        else:
            main = target_info[0]
            sub = ""
        with ctx.cd(main):
            ctx.run(f"python manage.py test {sub}", echo=True, pty=True)
