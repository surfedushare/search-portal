from invoke import Collection
from invoke.config import Config
from fabric import task

from environments.surfpol import create_configuration_and_session
from postgres.tasks_remote import restore_snapshot, setup_postgres, create_snapshot
from commands.projects.harvester.fabric import create_super_user, connect_uwsgi, connect_flower
from legacy import download_database


environment, session = create_configuration_and_session(use_aws_default_profile=False, config_class=Config)


@task(name="setup")
def setup_bastion(ctx):
    ctx.sudo("apt-get install -y awscli", echo=True)  # TODO: add commands we really need


namespace = Collection(
    Collection("bastion", setup_bastion),
    Collection("db", setup_postgres, restore_snapshot, create_snapshot),
    Collection("hrv", create_super_user, connect_uwsgi, connect_flower),
    Collection("legacy", download_database),
)
namespace.configure(environment)
