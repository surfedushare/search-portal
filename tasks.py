from invoke import Collection

from environments.surfpol import create_configuration_and_session
from elastic.tasks import setup, create_snapshot, load_repository, restore_snapshot
from deploy import prepare_builds, build, push, deploy, migrate
from test import e2e_tests, harvester_tests, service_tests, elastic_search_tests, test
from postgres.tasks import import_snapshot as postgres_import_snapshot


environment, session = create_configuration_and_session(use_aws_default_profile=False)


namespace = Collection(
    Collection("es", setup, create_snapshot, load_repository, restore_snapshot),
    Collection("db", postgres_import_snapshot),
    prepare_builds,
    build,
    push,
    deploy,
    migrate,
    e2e_tests,
    service_tests,
    harvester_tests,
    elastic_search_tests,
    test
)
namespace.configure(environment)
