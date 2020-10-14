from invoke import Collection

from environments.surfpol import create_configuration_and_session
from commands.deploy import prepare_builds, build, push, deploy, migrate
from commands.test import test_collection
from commands.postgres.invoke import import_snapshot as postgres_import_snapshot
from commands.projects.harvester.invoke import setup_harvester, import_dataset, harvest, cleanup
from service.tasks_local import setup_service
from legacy import upload_database, download_media, upload_media


environment, session = create_configuration_and_session(use_aws_default_profile=False)


namespace = Collection(
    Collection("db", postgres_import_snapshot),
    Collection("srv", setup_service),
    Collection("hrv", setup_harvester, import_dataset, harvest, cleanup),
    Collection("legacy", upload_database, download_media, upload_media),
    prepare_builds,
    build,
    push,
    deploy,
    migrate,
    test_collection
)
namespace.configure(environment)
