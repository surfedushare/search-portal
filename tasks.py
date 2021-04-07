from invoke import Collection

from environments.surfpol import create_configuration_and_session
from commands.postgres.invoke import setup_postgres_localhost
from commands.elastic.tasks import create_decompound_dictionary, push_decompound_dictionary
from commands.deploy import prepare_builds, build, push, deploy, migrate
from commands.test import test_collection
from commands.projects.service.invoke import import_snapshot, sync_upload_media, sync_category_filters
from commands.projects.harvester.invoke import (import_dataset, harvest, cleanup, index_dataset_version,
                                                dump_data, sync_harvest_content, generate_previews)


service_environment, _ = create_configuration_and_session(use_aws_default_profile=False, project="service")
service_collection = Collection("srv", setup_postgres_localhost, import_snapshot, deploy, sync_upload_media,
                                sync_category_filters)
service_collection.configure(service_environment)
aws_collection = Collection("aws", build, push, migrate)
aws_collection.configure(service_environment)


harvester_environment, _ = create_configuration_and_session(use_aws_default_profile=False, project="harvester")
harvester_collection = Collection("hrv", setup_postgres_localhost, harvest, cleanup, import_dataset, deploy,
                                  index_dataset_version, dump_data, sync_harvest_content,
                                  create_decompound_dictionary, push_decompound_dictionary, generate_previews)
harvester_collection.configure(harvester_environment)


namespace = Collection(
    service_collection,
    harvester_collection,
    aws_collection,
    prepare_builds,
    test_collection,
)
