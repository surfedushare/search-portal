from invoke import Collection
from invoke.config import Config
from fabric import task

from environments.surfpol import create_configuration_and_session


environment, session = create_configuration_and_session(use_aws_default_profile=False, config_class=Config)


@task(name="setup")
def setup_bastion(ctx):
    ctx.sudo("apt-get install -y postgresql-client", echo=True)


namespace = Collection(
    Collection("bastion", setup_bastion),
)
namespace.configure(environment)
