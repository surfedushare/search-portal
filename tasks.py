from invoke import Collection

from environments.surfpol import environment
from elastic.tasks import setup, create_snapshot, load_repository, restore_snapshot
from deploy import prepare_builds, build, push, deploy
from test import e2e_tests, harvester_tests, service_tests, vendor_tests, test


namespace = Collection(
    Collection("es", setup, create_snapshot, load_repository, restore_snapshot),
    prepare_builds,
    build,
    push,
    deploy,
    e2e_tests,
    service_tests,
    harvester_tests,
    vendor_tests,
    test
)
namespace.configure(environment)
