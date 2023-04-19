"""
This module exposes utilities to handle environment specific configuration.
The idea is that configuration is managed by just three environment variables:
 * APPLICATION_MODE (exposed as MODE)
 * APPLICATION_CONTEXT (exposed as CONTEXT)
 * APPLICATION_PROJECT (exposed as PROJECT)
The first specifies a mode like "production", "acceptance" or "development".
The second specifies where the code is run either "host" or "container"
The third indicates which project specific configuration to load.

Any configuration that you want to override can be set by using environment variables prefixed with "POL_".
For instance: if you want to override the django.debug configuration set POL_DJANGO_DEBUG=0.
If you leave empty any POL environment variables they are assumed to be unset. Use "0" for a False value.

Parts of the configuration is identical across environments
except for the environment prefix like "dev", "acc" and "prod" or the Amazon account id.
For these configurations the aws.py file in this file holds configuration templates,
that can be filled out with the prefix or account id.
All secrets are configuration templates that need an account id,
but these secret ARN's get swapped for their secret values as well.
"""
import os
import json
from invoke.config import Config
import boto3
import requests
from data_engineering.aws import (AWS_ENVIRONMENT_CONFIGURATIONS, AWS_ACCOUNT_CONFIGURATIONS, AWS_SECRET_CONFIGURATIONS,
                                  ENVIRONMENT_NAMES_TO_CODES, ENVIRONMENT_NAMES_TO_ACCOUNT_IDS)


MODE = os.environ.get("APPLICATION_MODE", "production")
MODE_PREFIX = "prod" if MODE == "production" else MODE[:3]
CONTEXT = os.environ.get("APPLICATION_CONTEXT", "container")
PROJECT = os.environ.get("APPLICATION_PROJECT", "edusources")
ECS_CONTAINER_METADATA_URI = os.environ.get("ECS_CONTAINER_METADATA_URI", None)

PREFIX = "POL"
ENVIRONMENTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# TODO: move these into the invoke.yml file
REPOSITORY = "017973353230.dkr.ecr.eu-central-1.amazonaws.com"
REPOSITORY_AWS_PROFILE = "pol-prod"
FARGATE_CLUSTER_NAME = "data-engineering"


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

    def load_project(self, merge=True):
        self._load_file(prefix="project", absolute=True, merge=merge)


def build_configuration_defaults(environment):
    environment_code = ENVIRONMENT_NAMES_TO_CODES[environment]
    account_id = ENVIRONMENT_NAMES_TO_ACCOUNT_IDS[environment]
    # Formatting configuration templates with prefix and account_id
    defaults = {
        "service": {
            "env": environment,
        },
        "aws": {
            "account": account_id,
            "environment_code": environment_code,
            "production": {
                "account": "017973353230",
                "profile_name": "pol-prod"
            }
        },
        "secrets": dict()
    }
    defaults["aws"].update({
        config: template.format(environment_code)
        for config, template in AWS_ENVIRONMENT_CONFIGURATIONS.items()
    })
    defaults["aws"].update({
        config: template.format(account_id)
        for config, template in AWS_ACCOUNT_CONFIGURATIONS.items()
    })
    for config, secrets in AWS_SECRET_CONFIGURATIONS.items():
        defaults["secrets"][config] = {
            secret: template.format(account_id) if template is not None else template
            for secret, template in secrets.items()
        }
    # We'll fetch the container metadata.
    # For more background on ECS_CONTAINER_METADATA_URI read:
    # https://docs.aws.amazon.com/AmazonECS/latest/userguide/task-metadata-endpoint-v3-fargate.html
    container_metadata = {}
    if ECS_CONTAINER_METADATA_URI:
        response = requests.get(ECS_CONTAINER_METADATA_URI)
        if response.status_code == 200:
            container_metadata = response.json()
    # Adding container specific information as configuration for reference in the application
    defaults.update({
        "container": {
            "id": container_metadata.get("DockerId", None),
            "family": container_metadata.get("family", None)
        }
    })
    # Returning results
    return defaults


def create_configuration(mode=None, context="container"):
    """
    We're using invoke Config as base for our configuration:
    http://docs.pyinvoke.org/en/stable/concepts/configuration.html#config-hierarchy.
    Since the config is created outside of invoke it works slightly different than normal.
    First we load configuration templates from aws.py through user configuration and build_container_overrides.
    The system invoke files are the common configuration files.
    The project invoke file contains configuration specific to "edusources" or "publinova".
    Runtime configurations are used to load superuser configurations and are set only in a host context.
    Shell environment variables override all other configuration.

    :param mode: the mode you want a configuration for
    :param context: the context you want a configuration for (host or container)
    :return: invoke configuration
    """
    mode = mode or MODE
    configuration_directory = os.path.join(ENVIRONMENTS, "data_engineering")
    config = POLConfig(
        defaults=build_configuration_defaults(mode),
        system_prefix=os.path.join(configuration_directory, mode) + os.path.sep,
        lazy=True
    )
    config._project_path = os.path.join(configuration_directory, f"{PROJECT}.yml")
    if context != "container":
        config.set_runtime_path(os.path.join(configuration_directory, mode, f"superuser.invoke.yml"))
    config.load_system()
    config.load_user()
    config.load_project()
    config.load_runtime()
    config.load_shell_env()
    return config


def create_configuration_and_session():
    """
    Creates an environment holding all the configuration for current mode and creates an AWS session.
    The used profile for AWS session is either default or the configured profile_name for the environment

    :param config_class: Set to invoke.config.Config if you want to use Fabric
    :param service: The name of the service to get the environment for
    :return: environment, session
    """

    # Now we use the customize invoke load as described above
    environment = create_configuration(MODE, context=CONTEXT)
    # Creating a AWS session based on configuration and context
    session = boto3.Session() if CONTEXT != "host" else boto3.Session(profile_name=environment.aws.profile_name)

    # Load secrets (we resolve secrets during runtime so that AWS can manage them)
    # This skips over any non-AWS secrets
    if environment.aws.load_secrets:
        secrets = environment.secrets or {}
        aws_secrets = []
        for group_name, group_secrets in secrets.items():
            for secret_name, secret_id in group_secrets.items():
                if secret_id is not None and secret_id.startswith("arn:aws:secretsmanager"):
                    aws_secrets.append((group_name, secret_name, secret_id,))
        # Here we found AWS secrets which we load using boto3
        if aws_secrets and CONTEXT != "unprivileged":
            secrets_manager = session.client('secretsmanager')
            for group_name, secret_name, secret_id in aws_secrets:
                secret_value = secrets_manager.get_secret_value(SecretId=secret_id)
                secret_payload = json.loads(secret_value["SecretString"])
                secrets[group_name][secret_name] = secret_payload[secret_name]

    return environment, session
