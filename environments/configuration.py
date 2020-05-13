"""
This module exposes the environment which is an invoke Config that holds environment specific configuration.
The idea is that all configuration is managed by just two environment variables:
 * APPLICATION_MODE
 * APPLICATION_CONTEXT
The first specifies a mode like "production", "acceptance" or "development".
The latter specifies how the configuration files are found. Inside a Docker container or outside of them.
Read more about invoke Config here: http://docs.pyinvoke.org/en/stable/concepts/configuration.html#config-hierarchy

Since the config is created outside of invoke it works slightly differently than normal.
The system invoke files are the environment configuration files.
For the rest the project and shell environment variables get loaded as normal and may override environments.
"""
import os
import json
from invoke.config import Config
import boto3

# First we'll load the relevant non-invoke environment variables
MODE = os.environ.get("APPLICATION_MODE", "production")
CONTEXT = os.environ.get("APPLICATION_CONTEXT", "container")
PREFIX = "POL"
ENVIRONMENTS = os.path.dirname(os.path.abspath(__file__))
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


# Now we use the customize invoke load as described above
environment = POLConfig(
    system_prefix=MODE_ENVIRONMENT + os.path.sep
)
environment.load_system()
environment.load_user()
environment.load_project()
environment.load_shell_env()


# Load computed overrides (we post process to prevent setting some variables everywhere)
database_credentials = environment.postgres.credentials
if database_credentials:
    user, password = database_credentials.split(":")
    environment.load_overrides({
        "django": {
            "postgres_user": user,
            "postgres_password": password
        }
    })


# Load secrets (we resolve secrets during runtime so that AWS can manage them)
# This skips over any non-AWS secrets
secrets = environment.secrets or {}
aws_secrets = []
for group_name, group_secrets in secrets.items():
    for secret_name, secret_id in group_secrets.items():
        if secret_id is not None and secret_id.startswith("arn:aws:secretsmanager"):
            aws_secrets.append((group_name, secret_name, secret_id,))
# Here we found AWS secrets which we load using boto3
if aws_secrets:
    secrets_manager = boto3.client('secretsmanager')
    for group_name, secret_name, secret_id in aws_secrets:
        secret_value = secrets_manager.get_secret_value(SecretId=secret_id)
        secret_payload = json.loads(secret_value["SecretString"])
        secrets[group_name][secret_name] = secret_payload[secret_name]
