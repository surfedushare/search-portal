from invoke import Collection

from environments.project import create_configuration_and_session as service_configuration_and_session
from environments.data_engineering.configuration import create_configuration_and_session, TEAM
from commands.postgres.invoke import setup_postgres_localhost
from commands.opensearch.tasks import (create_decompound_dictionary, push_decompound_dictionary, push_indices_template,
                                       recreate_test_indices)
from commands.aws.ecs import cleanup_ecs_artifacts
from commands.aws.repository import sync_repository_state
from commands.deploy import (prepare_builds, build, push, deploy, migrate, promote, print_available_images,
                             publish_runner_image, publish_tika_image)
from commands.test import test_collection
from commands.services.service.invoke import (import_snapshot, sync_upload_media, make_translations)
from commands.services.harvester.invoke import (load_data, harvest, clean_data, index_dataset_version,
                                                dump_data, sync_harvest_content, generate_previews,
                                                promote_dataset_version, extend_resource_cache, sync_preview_media,
                                                sync_metadata, harvester_migrate)


service_environment, _ = service_configuration_and_session(service="service")
service_collection = Collection("srv", setup_postgres_localhost, import_snapshot, deploy, sync_upload_media,
                                make_translations, recreate_test_indices)
service_collection.configure(service_environment)


harvester_environment, _ = create_configuration_and_session()
harvester_collection = Collection("hrv", setup_postgres_localhost, harvest, clean_data, load_data, deploy,
                                  index_dataset_version, dump_data, sync_harvest_content, promote_dataset_version,
                                  create_decompound_dictionary, push_decompound_dictionary, generate_previews,
                                  extend_resource_cache, sync_preview_media, sync_metadata, push_indices_template,
                                  harvester_migrate)
harvester_collection.configure(harvester_environment)


aws_collection = Collection("aws", build, push, migrate, promote, print_available_images,
                            sync_repository_state, publish_runner_image, cleanup_ecs_artifacts, publish_tika_image)


if TEAM == "web":
    aws_collection.configure(service_environment)
    test_collection.configure(service_environment)
else:
    aws_collection.configure(harvester_environment)
    test_collection.configure(harvester_environment)


namespace = Collection(
    service_collection,
    harvester_collection,
    aws_collection,
    prepare_builds,
    test_collection,
)
