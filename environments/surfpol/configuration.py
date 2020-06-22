"""
This module exposes utilities to handle environment specific configuration for all Python projects in this repo.
The idea is that configuration across projects is managed by just two environment variables:
 * APPLICATION_MODE (exposed as MODE)
 * APPLICATION_CONTEXT (exposed as CONTEXT)
The first specifies a mode like "production", "acceptance" or "development".
The latter specifies where the code is run either "host" or "container"
Any configuration that you want to override can be set by using environment variables prefixed with "POL_".
For instance: if you want to override the django.debug configuration for acceptance set POL_DJANGO_DEBUG=0.
If you leave empty any POL environment variables they are assumed to be unset. Use "0" for a False value.

We're using invoke Config as base for our configuration:
http://docs.pyinvoke.org/en/stable/concepts/configuration.html#config-hierarchy.
Since the config is created outside of invoke it works slightly different than normal.
The system invoke files are the environment configuration files.
Runtime configurations are used to load superuser configurations and are set only in a host context.
Shell environment variables override all other configuration.
"""
import os
import json
from invoke.config import Config
import boto3


MODE = os.environ.get("APPLICATION_MODE", "production")
CONTEXT = os.environ.get("APPLICATION_CONTEXT", "container")

PREFIX = "POL"
ENVIRONMENTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODE_ENVIRONMENT = os.path.join(ENVIRONMENTS, MODE)


# Now we'll delete any items that are POL variables, but with empty values
# Use a value of "0" for a Boolean instead of an empty string
invalid_keys = []
for key, value in os.environ.items():
    if key.startswith(f"{PREFIX}_") and value == "":
        invalid_keys.append(key)
for key in invalid_keys:
    os.environ.pop(key)


# Using a custom configuration class
class POLConfig(Config):
    env_prefix = PREFIX


def create_configuration_and_session(use_aws_default_profile=True, config_class=POLConfig):
    """
    Creates an environment holding all the configuration for current mode and creates an AWS session.
    The used profile for AWS session is either default or the configured profile_name for the environment

    :param use_aws_default_profile: Set to false when you want to load environment specific AWS profile
    :param config_class: Set to invoke.config.Config if you want to use Fabric
    :return: environment, session
    """

    # Now we use the customize invoke load as described above
    environment = config_class(
        system_prefix=MODE_ENVIRONMENT + os.path.sep,
        user_prefix=os.path.join(MODE_ENVIRONMENT, "superuser.") if CONTEXT == "host" else None
    )
    environment.load_system()
    environment.load_user()
    environment.load_project()
    environment.load_shell_env()
    environment.load_runtime()

    # Creating a AWS session based on configuration and context
    session = boto3.Session() if use_aws_default_profile else boto3.Session(profile_name=environment.aws.profile_name)

    # Load secrets (we resolve secrets during runtime so that AWS can manage them)
    # This skips over any non-AWS secrets (localhost only)
    secrets = environment.secrets or {}
    aws_secrets = []
    for group_name, group_secrets in secrets.items():
        for secret_name, secret_id in group_secrets.items():
            if secret_id is not None and secret_id.startswith("arn:aws:secretsmanager"):
                aws_secrets.append((group_name, secret_name, secret_id,))
    # Here we found AWS secrets which we load using boto3
    if aws_secrets:
        secrets_manager = session.client('secretsmanager')
        for group_name, secret_name, secret_id in aws_secrets:
            secret_value = secrets_manager.get_secret_value(SecretId=secret_id)
            secret_payload = json.loads(secret_value["SecretString"])
            secrets[group_name][secret_name] = secret_payload[secret_name]

    return environment, session
