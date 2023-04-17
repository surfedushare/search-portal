from invoke import Collection
from invoke.config import Config
from fabric import Config
from environments.project import create_configuration_and_session as service_configuration_and_session
from environments.data_engineering.configuration import create_configuration_and_session
from commands.postgres.fabric import setup_postgres_remote
from commands.services.service.fabric import create_snapshot, restore_snapshot
from commands.services.harvester.fabric import connect_with_shell


service_environment, _ = service_configuration_and_session(
    config_class=Config,
    service="service"
)
service_collection = Collection("srv", setup_postgres_remote, create_snapshot, restore_snapshot, connect_with_shell)
service_collection.configure(service_environment)


harvester_environment, _ = create_configuration_and_session()
harvester_collection = Collection("hrv", setup_postgres_remote, connect_with_shell)
harvester_collection.configure(harvester_environment)


namespace = Collection(
    service_collection,
    harvester_collection,
)
