"""
A configuration for AWS can take three forms
1)   The configuration specifies dev, acc or prod. These are "environment" configurations.
2)   The configuration specifies an AWS account id. These are "account" configurations.
3)   The configuration is an AWS Secrets Manager ARN. These need to be replaced with the actual secrets.

This file lists all different types of AWS configuration.
In such a way that it is easy to format them with either "environment" or "account" information.
And further processing if it involves a secret that needs fetching.

The final configuration are available under the "aws" or "secrets" attributes of the invoke Config object.
"""

ENVIRONMENT_NAMES_TO_CODES = {
    "localhost": "dev",
    "development": "dev",
    "acceptance": "acc",
    "production": "prod"
}

ENVIRONMENT_NAMES_TO_ACCOUNT_IDS = {
    "localhost": "322480324822",
    "development": "322480324822",
    "acceptance": "000428825067",
    "production": "017973353230"
}

AWS_ENVIRONMENT_CONFIGURATIONS = {
    "bastion": "bastion.{environment_code}.surfedushare.nl",
    "profile_name": "pol-{environment_code}",
}

AWS_ACCOUNT_CONFIGURATIONS = {
    "superuser_task_role_arn": "arn:aws:iam::{account}:role/detSuperuserTaskExecutionRole",
    "postgres_password_arn": "arn:aws:secretsmanager:eu-central-1:{account}:secret:postgres",
    "task_role_arn": "arn:aws:iam::{account}:role/detHarvesterTaskExecutionRole",
}

AWS_SECRET_CONFIGURATIONS = {
    "postgres": {
        "password": "arn:aws:secretsmanager:eu-central-1:{account}:secret:harvester/postgres-application",
        "application_password": "arn:aws:secretsmanager:eu-central-1:{account}:secret:harvester/postgres-application",
    },
    "opensearch": {
        "password": "arn:aws:secretsmanager:eu-central-1:{account}:secret:opensearch/password",
    },
    "django": {
        "secret_key": "arn:aws:secretsmanager:eu-central-1:{account}:secret:harvester/django",
        "admin_password": "arn:aws:secretsmanager:eu-central-1:{account}:secret:harvester/django",
    },
    "sharekit": {
        "api_key": "arn:aws:secretsmanager:eu-central-1:{account}:secret:credentials/sharekit",
    },
    "harvester": {
        "api_key": "arn:aws:secretsmanager:eu-central-1:{account}:secret:harvester/credentials",
        "webhook_secret": "arn:aws:secretsmanager:eu-central-1:{account}:secret:harvester/credentials",
    },
    "matomo": {
        "api_key": "arn:aws:secretsmanager:eu-central-1:{account}:secret:harvester/matomo-api-key",
    },
    "eduterm": {
        "api_key": "arn:aws:secretsmanager:eu-central-1:{account}:secret:eduterm",
    },
    "deepl": {
        "api_key": "arn:aws:secretsmanager:eu-central-1:{account}:secret:search-portal/deepl",
    },
    "teams_webhooks": {
        "harvester": "arn:aws:secretsmanager:eu-central-1:{account}:secret:harvester/teams-webhooks",
    },
    "hanze": {
        "api_key": "arn:aws:secretsmanager:eu-central-1:{account}:secret:credentials/hanze",
    },
    "hva": {
        "api_key": "arn:aws:secretsmanager:eu-central-1:{account}:secret:credentials/hva",
    },
    "buas": {
        "api_key": "arn:aws:secretsmanager:eu-central-1:{account}:secret:credentials/buas",
    },
}
