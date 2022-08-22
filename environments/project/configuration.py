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
ECS_CONTAINER_METADATA_URI = os.environ.get("ECS_CONTAINER_METADATA_URI", None)

PREFIX = "POL"
ENVIRONMENTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Some dynamic configuration depends on the project and we load that module here
sys.path.append(ENVIRONMENTS)
project_configuration = importlib.import_module(f"{PROJECT}.configuration")
REPOSITORY = project_configuration.REPOSITORY
REPOSITORY_AWS_PROFILE = project_configuration.REPOSITORY_AWS_PROFILE
FARGATE_CLUSTER_NAME = project_configuration.FARGATE_CLUSTER_NAME
SEARCH_FIELDS = project_configuration.SEARCH_FIELDS


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


def create_open_search_index_configuration(lang, decompound_word_list=None):
    language_analyzers = {
        'nl': 'custom_dutch',
        'en': 'english'
    }
    search_analyzer = language_analyzers.get(lang, "standard")
    if decompound_word_list and lang == "nl":
        search_analyzer = "dutch_dictionary_decompound"
    configuration = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "analysis": {
                "analyzer": {
                    "trigram": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "shingle"]
                    },
                    "folding": {
                        "tokenizer": "standard",
                        "filter":  ["lowercase", "asciifolding"]
                    },
                    "custom_dutch": {
                        "tokenizer":  "standard",
                        "filter": [
                            "lowercase",
                            "dutch_stop",
                            "dutch_keywords",
                            "dutch_override",
                            "dutch_stemmer",
                        ]
                    },
                },
                "filter": {
                    "dutch_stop": {
                        "type": "stop",
                        "stopwords": "_dutch_"
                    },
                    "shingle": {
                        "type": "shingle",
                        "min_shingle_size": 2,
                        "max_shingle_size": 3
                    },
                    "dutch_keywords": {
                        "type":       "keyword_marker",
                        "keywords":   ["palliatieve"]
                    },
                    "dutch_stemmer": {
                        "type":       "stemmer",
                        "language":   "dutch"
                    },
                    "dutch_override": {
                        "type":       "stemmer_override",
                        "rules": []
                    },
                    "dutch_synonym": {
                        "type": "synonym_graph",
                        "synonyms": [
                            "palliatie, palliatieve"
                        ]
                    }
                }
            }
        },
        'mappings': {
            'properties': {
                'title': {
                    'type': 'text',
                    'fields': {
                        'analyzed': {
                            'type': 'text',
                            'analyzer': language_analyzers.get(lang, "standard"),
                            'search_analyzer': search_analyzer,
                        },
                        'folded': {
                            'type': 'text',
                            'analyzer': 'folding'
                        }
                    }
                },
                'text': {
                    'type': 'text',
                    'fields': {
                        'analyzed': {
                            'type': 'text',
                            'analyzer': language_analyzers.get(lang, "standard"),
                            'search_analyzer': search_analyzer,
                        },
                        'folded': {
                            'type': 'text',
                            'analyzer': 'folding'
                        }
                    }
                },
                'description': {
                    'type': 'text',
                    'fields': {
                        'analyzed': {
                            'type': 'text',
                            'analyzer': language_analyzers.get(lang, "standard"),
                            'search_analyzer': search_analyzer,
                        },
                        'folded': {
                            'type': 'text',
                            'analyzer': 'folding'
                        }
                    }
                },
                'url': {'type': 'text'},
                'authors': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'text',
                            'fields': {
                                'keyword': {
                                    'type': 'keyword',
                                    'ignore_above': 256
                                },
                                'folded': {
                                    'type': 'text',
                                    'analyzer': 'folding'
                                }
                            }
                        },
                        'email': {
                            'type': 'keyword'
                        },
                        'external_id': {
                            'type': 'keyword'
                        },
                        'dai': {
                            'type': 'keyword'
                        },
                        'orcid': {
                            'type': 'keyword'
                        },
                        'isni': {
                            'type': 'keyword'
                        }
                    }
                },
                'publishers': {
                    'type': 'text',
                    'fields': {
                        'keyword': {
                            'type': 'keyword',
                            'ignore_above': 256
                        },
                        'folded': {
                            'type': 'text',
                            'analyzer': 'folding'
                        }
                    }
                },
                'publisher_date': {
                    'type': 'date',
                    'format': 'strict_date_optional_time||yyyy-MM||epoch_millis'
                },
                'publisher_year': {
                    'type': 'keyword'
                },
                'keywords': {
                    'type': 'text',
                    'fields': {
                        'keyword': {
                            'type': 'keyword',
                            'ignore_above': 256
                        },
                        'folded': {
                            'type': 'text',
                            'analyzer': 'folding'
                        }
                    }
                },
                'technical_type': {
                    'type': 'keyword'
                },
                'id': {'type': 'text'},
                'external_id': {
                    'type': 'keyword'
                },
                'harvest_source': {
                    'type': 'keyword'
                },
                "suggest_completion": {
                    "type": "completion"
                },
                "suggest_phrase": {
                    "type": "text",
                    "analyzer": "trigram"
                },
                'is_part_of': {
                    'type': 'keyword'
                },
                'has_parts': {
                    'type': 'keyword'
                }
            }
        }
    }

    # Update the mapping properties with the project configuration
    configuration["mappings"]["properties"].update(project_configuration.get_project_search_mapping_properties())

    # Then if our (AWS) environment supports it we add decompound settings
    if decompound_word_list:
        configuration["settings"]["analysis"]["analyzer"]["dutch_dictionary_decompound"] = {
            "type": "custom",
            "tokenizer": "standard",
            "filter": ["lowercase", "dutch_stop", "dutch_synonym", "dictionary_decompound"]
        }
        configuration["settings"]["analysis"]["filter"]["dictionary_decompound"] = {
            "type": "dictionary_decompounder",
            "word_list_path": decompound_word_list,
            "updateable": True
        }

    return configuration
