from invoke import Collection

from environments.surfpol import create_configuration_and_session
from commands.postgres.invoke import setup_postgres_localhost
from commands.deploy import prepare_builds, build, push, deploy, migrate
from commands.test import test_collection
from commands.projects.service.invoke import import_snapshot
from commands.projects.harvester.invoke import import_dataset, harvest, cleanup
from legacy import download_media, upload_media


service_environment, _ = create_configuration_and_session(use_aws_default_profile=False, project="service")
service_collection = Collection("srv", setup_postgres_localhost, import_snapshot)
service_collection.configure(service_environment)
legacy_collection = Collection("legacy", download_media, upload_media)
legacy_collection.configure(service_environment)


harvester_environment, _ = create_configuration_and_session(use_aws_default_profile=False, project="harvester")
harvester_collection = Collection("hrv", setup_postgres_localhost, harvest, cleanup, import_dataset)
harvester_collection.configure(harvester_environment)


namespace = Collection(
    service_collection,
    harvester_collection,
    legacy_collection,
    prepare_builds,
    build,
    push,
    deploy,
    migrate,
    test_collection
)
