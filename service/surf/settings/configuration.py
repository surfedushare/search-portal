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
from invoke.config import Config


MODE = os.environ.get("APPLICATION_MODE", "production")
CONTEXT = os.environ.get("APPLICATION_CONTEXT", "container")

BASE_ENVIRONMENT = "/usr/etc/pol" if CONTEXT == "container" else "../environments"
MODE_ENVIRONMENT = os.path.join(BASE_ENVIRONMENT, MODE)


class POLConfig(Config):
    env_prefix = "POL"


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
