"""
This module exposes utilities to handle environment specific configuration for all Python services in this repo.
The idea is that configuration across services is managed by just two environment variables:
 * APPLICATION_MODE (exposed as MODE)
 * APPLICATION_CONTEXT (exposed as CONTEXT)
The first specifies a mode like "production", "acceptance" or "development".
The latter specifies where the code is run either "host" or "container"
Any configuration that you want to override can be set by using environment variables prefixed with "POL_".
For instance: if you want to override the django.debug configuration for acceptance set POL_DJANGO_DEBUG=0.
If you leave empty any POL environment variables they are assumed to be unset. Use "0" for a False value.
"""
import os
import json
from invoke.config import Config
import boto3
import requests
import importlib
import sys


MODE = os.environ.get("APPLICATION_MODE", "production")
CONTEXT = os.environ.get("APPLICATION_CONTEXT", "container")
PROJECT = os.environ.get("APPLICATION_PROJECT", "edusources")
if PROJECT == "publinova":
    PROJECT = "nppo"
if PROJECT == "nppo" and MODE == "development":
    MODE = "acceptance"
ECS_CONTAINER_METADATA_URI = os.environ.get("ECS_CONTAINER_METADATA_URI", None)

PREFIX = "POL"
ENVIRONMENTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENVIRONMENT_NAMES_TO_CODES = {
    "localhost": "dev",
    "development": "dev",
    "acceptance": "acc",
    "production": "prod"
}


# Some dynamic configuration depends on the project and we load that module here
sys.path.append(ENVIRONMENTS)
project_configuration = importlib.import_module(f"{PROJECT}.configuration")
REPOSITORY = project_configuration.REPOSITORY
REPOSITORY_AWS_PROFILE = project_configuration.REPOSITORY_AWS_PROFILE
FARGATE_CLUSTER_NAME = project_configuration.FARGATE_CLUSTER_NAME


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


def build_configuration_defaults(environment):
    environment_code = ENVIRONMENT_NAMES_TO_CODES[environment]
    production_account_id = REPOSITORY.split(".")[0]
    defaults = POLConfig.global_defaults()
    defaults.update({
        "project": {
            "name": PROJECT
        },
        "service": {
            "env": environment,
            "deploy": {
                "tags": {
                    "central": environment_code
                }
            }
        },
        "aws": {
            "environment_code": environment_code,
            "cluster_name": FARGATE_CLUSTER_NAME,
            "production": {
                "account": production_account_id,
                "profile_name": REPOSITORY_AWS_PROFILE,
                "registry": REPOSITORY
            },
            "repositories": ["harvester", "harvester-nginx", "search-portal", "search-portal-nginx"],
            "task_definition_families": ["harvester", "search-portal", "celery", "harvester-command"]
        },
        "secrets": dict()
    })
    return defaults


def create_configuration(mode, service=None, context="container", config_class=POLConfig):
    """
    We're using invoke Config as base for our configuration:
    http://docs.pyinvoke.org/en/stable/concepts/configuration.html#config-hierarchy.
    Since the config is created outside of invoke it works slightly different than normal.
    The system invoke files are the environment configuration files.
    Runtime configurations are used to load superuser configurations and are set only in a host context.
    Shell environment variables override all other configuration.

    :param mode: the mode you want a configuration for
    :param service: the service you want a configuration for (service or harvester)
    :param context: the context you want a configuration for (host or container)
    :param config_class: Which configuration class to use (default is POLConfig)
    :return: configuration
    """
    mode_environment = os.path.join(ENVIRONMENTS, PROJECT, mode)
    config = config_class(
        defaults=build_configuration_defaults(mode),
        system_prefix=mode_environment + os.path.sep,
        runtime_path=os.path.join(mode_environment, "superuser.invoke.yml") if context != "container" else None,
        project_location=os.path.join(mode_environment, service) if service else None,
        lazy=True
    )
    config.load_system()
    config.load_user()
    config.load_project()
    config.load_shell_env()
    config.load_runtime()

    # See: https://docs.aws.amazon.com/AmazonECS/latest/userguide/task-metadata-endpoint-v3-fargate.html
    container_metadata = {}
    if ECS_CONTAINER_METADATA_URI:
        response = requests.get(ECS_CONTAINER_METADATA_URI)
        if response.status_code == 200:
            container_metadata = response.json()
        else:
            container_metadata = {
                "status_code": response.status_code,
                "reason": response.reason
            }
    config.load_overrides({
        "container": {
            "id": container_metadata.get("DockerId", None),
            "family": container_metadata.get("family", None)
        }
    })

    return config


def create_configuration_and_session(config_class=POLConfig, service=None):
    """
    Creates an environment holding all the configuration for current mode and creates an AWS session.
    The used profile for AWS session is either default or the configured profile_name for the environment

    :param config_class: Set to invoke.config.Config if you want to use Fabric
    :param service: The name of the service to get the environment for
    :return: environment, session
    """

    # Now we use the customize invoke load as described above
    environment = create_configuration(MODE, service=service, context=CONTEXT, config_class=config_class)

    # Creating a AWS session based on configuration and context
    session = boto3.Session() if CONTEXT != "host" else boto3.Session(profile_name=environment.aws.profile_name)

    # Load secrets (we resolve secrets during runtime so that AWS can manage them)
    # This skips over any non-AWS secrets (localhost only)
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
