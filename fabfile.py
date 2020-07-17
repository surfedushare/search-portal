from invoke import Collection
from invoke.config import Config
from fabric import task

from environments.surfpol import create_configuration_and_session
from postgres.tasks_remote import restore_snapshot, setup as postgres_setup
from harvester.tasks_remote import create_super_user, connect_uwsgi


environment, session = create_configuration_and_session(use_aws_default_profile=False, config_class=Config)


@task(name="setup")
def setup_bastion(ctx):
    ctx.sudo("apt-get install -y awscli", echo=True)  # TODO: add commands we really need


namespace = Collection(
    Collection("bastion", setup_bastion),
    Collection("db", postgres_setup, restore_snapshot),
    Collection("hrv", create_super_user, connect_uwsgi),
)
namespace.configure(environment)
