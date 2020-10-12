from invoke import Collection

from environments.surfpol import create_configuration_and_session
from elastic.tasks import setup, create_snapshot, load_repository, restore_snapshot
from deploy import prepare_builds, build, push, deploy, migrate
from test import e2e_tests, harvester_tests, service_tests, elastic_search_tests, test
from postgres.tasks_local import import_snapshot as postgres_import_snapshot
from commands.projects.harvester.invoke import setup_harvester, import_dataset, harvest, cleanup
from service.tasks_local import setup_service
from legacy import upload_database, download_media, upload_media


environment, session = create_configuration_and_session(use_aws_default_profile=False)


namespace = Collection(
    Collection("es", setup, create_snapshot, load_repository, restore_snapshot),
    Collection("db", postgres_import_snapshot),
    Collection("srv", setup_service),
    Collection("hrv", setup_harvester, import_dataset, harvest, cleanup),
    Collection("legacy", upload_database, download_media, upload_media),
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
