from invoke import Collection
from invoke.config import Config

from environments.surfpol import create_configuration_and_session
from commands.postgres.fabric import setup_postgres_remote
from commands.elastic.fabric import connect_elastic_cluster
from commands.projects.service.fabric import create_snapshot, restore_snapshot
from commands.projects.harvester.fabric import connect_uwsgi, connect_flower
from commands.legacy import download_database, upload_database


service_environment, _ = create_configuration_and_session(
    use_aws_default_profile=False,
    config_class=Config,
    project="service"
)
service_collection = Collection("srv", setup_postgres_remote, create_snapshot, restore_snapshot)
service_collection.configure(service_environment)
legacy_collection = Collection("legacy", download_database, upload_database)
legacy_collection.configure(service_environment)


harvester_environment, _ = create_configuration_and_session(
    use_aws_default_profile=False,
    config_class=Config,
    project="harvester"
)
harvester_collection = Collection("hrv", setup_postgres_remote, connect_uwsgi, connect_flower)
harvester_collection.configure(harvester_environment)
elastic_connection = Collection("aws", connect_elastic_cluster)
elastic_connection.configure(harvester_environment)


namespace = Collection(
    elastic_connection,
    service_collection,
    harvester_collection,
    legacy_collection
)
