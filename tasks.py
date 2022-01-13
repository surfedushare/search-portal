from invoke import Collection

from environments.project import create_configuration_and_session
from commands.postgres.invoke import setup_postgres_localhost
from commands.elastic.tasks import create_decompound_dictionary, push_decompound_dictionary
from commands.deploy import (prepare_builds, build, push, deploy, migrate, print_available_images,
                             print_running_containers)
from commands.test import test_collection
from commands.services.service.invoke import (import_snapshot, sync_upload_media, sync_category_filters,
                                              make_translations)
from commands.services.harvester.invoke import (load_data, harvest, clean_data, index_dataset_version,
                                                dump_data, sync_harvest_content, generate_previews,
                                                promote_dataset_version, extend_resource_cache, sync_preview_media,
                                                sync_metadata)


service_environment, _ = create_configuration_and_session(use_aws_default_profile=False, service="service")
service_collection = Collection("srv", setup_postgres_localhost, import_snapshot, deploy, sync_upload_media,
                                sync_category_filters, make_translations)
service_collection.configure(service_environment)
aws_collection = Collection("aws", build, push, migrate, print_available_images, print_running_containers)
aws_collection.configure(service_environment)


harvester_environment, _ = create_configuration_and_session(use_aws_default_profile=False, service="harvester")
harvester_collection = Collection("hrv", setup_postgres_localhost, harvest, clean_data, load_data, deploy,
                                  index_dataset_version, dump_data, sync_harvest_content, promote_dataset_version,
                                  create_decompound_dictionary, push_decompound_dictionary, generate_previews,
                                  extend_resource_cache, sync_preview_media, sync_metadata)
harvester_collection.configure(harvester_environment)


namespace = Collection(
    service_collection,
    harvester_collection,
    aws_collection,
    prepare_builds,
    test_collection,
)
