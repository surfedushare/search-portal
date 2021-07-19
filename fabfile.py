from invoke import Collection
from invoke.config import Config

from environments.surfpol import create_configuration_and_session
from commands.postgres.fabric import setup_postgres_remote
from commands.elastic.fabric import connect_elastic_cluster, push_indices_template
from commands.services.service.fabric import create_snapshot, restore_snapshot
from commands.services.harvester.fabric import connect_uwsgi, connect_flower, connect_with_shell


service_environment, _ = create_configuration_and_session(
    use_aws_default_profile=False,
    config_class=Config,
    project="service"
)
service_collection = Collection("srv", setup_postgres_remote, create_snapshot, restore_snapshot, connect_with_shell)
service_collection.configure(service_environment)


harvester_environment, _ = create_configuration_and_session(
    use_aws_default_profile=False,
    config_class=Config,
    project="harvester"
)
harvester_collection = Collection("hrv", setup_postgres_remote, connect_uwsgi, connect_flower, connect_with_shell)
harvester_collection.configure(harvester_environment)
elastic_collection = Collection("aws", connect_elastic_cluster, push_indices_template)
elastic_collection.configure(harvester_environment)


namespace = Collection(
    elastic_collection,
    service_collection,
    harvester_collection,
)
