import os
import json

from invoke.tasks import task
from invoke.exceptions import Exit

from commands import TARGETS
from commands.aws.ecs import register_task_definition, build_default_container_variables
from commands.aws.utils import create_aws_session


def register_clearlogins_task(ctx, aws_config, task_definition_arn):
    session = create_aws_session(ctx.config.aws.profile_name)
    events_client = session.client('events')
    iam = session.resource('iam')
    role = iam.Role('ecsEventsRole')

    events_client.put_targets(
        Rule='clearlogins',
        Targets=[
            {
                'Id': '1',
                'Arn': aws_config.cluster_arn,
                'RoleArn': role.arn,
                'Input': json.dumps(
                    {
                        "containerOverrides": [
                            {
                                "name": "search-portal-container",
                                "command": ["python", "manage.py", "clearlogins"]
                            }
                        ]
                    }
                ),
                'EcsParameters': {
                    'TaskDefinitionArn': task_definition_arn,
                    'TaskCount': 1,
                    'LaunchType': 'FARGATE',
                    'NetworkConfiguration': {
                        "awsvpcConfiguration": {
                            "Subnets": [aws_config.private_subnet_id],
                            "SecurityGroups": [
                                aws_config.rds_security_group_id,
                                aws_config.default_security_group_id

                            ]
                        }
                    }
                }
            }
        ]
    )


def deploy_harvester(ctx, mode, ecs_client, task_role_arn, version):
    target_info = TARGETS["harvester"]
    harvester_container_variables = build_default_container_variables(mode, version)
    harvester_container_variables.update({
        "flower_secret_arn": ctx.config.aws.flower_secret_arn
    })

    harvester_task_definition_arn = register_task_definition(
        "harvester",
        ecs_client,
        task_role_arn,
        harvester_container_variables,
        os.path.join("harvester", "aws-container-definitions.json"),
        target_info["cpu"],
        target_info["memory"]
    )

    ecs_client.update_service(
        cluster=ctx.config.aws.cluster_arn,
        service="harvester",
        taskDefinition=harvester_task_definition_arn
    )

    celery_container_variables = build_default_container_variables(mode, version)
    celery_container_variables.update({
        "concurrency": "4"
    })

    celery_task_definition_arn = register_task_definition(
        "celery",
        ecs_client,
        task_role_arn,
        celery_container_variables,
        os.path.join("harvester", "celery-container-definitions.json"),
        target_info["celery_cpu"],
        target_info["celery_memory"]
    )

    ecs_client.update_service(
        cluster=ctx.config.aws.cluster_arn,
        service="celery",
        taskDefinition=celery_task_definition_arn
    )


def deploy_service(ctx, mode, ecs_client, task_role_arn, version):
    target_info = TARGETS["service"]
    service_container_variables = build_default_container_variables(mode, version)

    print("Registering task definition")
    service_task_definition_arn = register_task_definition(
        target_info['name'],
        ecs_client,
        task_role_arn,
        service_container_variables,
        os.path.join("service", "aws-container-definitions.json"),
        target_info["cpu"],
        target_info["memory"]
    )

    print("Updating service")
    ecs_client.update_service(
        cluster=ctx.config.aws.cluster_arn,
        service=target_info['name'],
        taskDefinition=service_task_definition_arn
    )

    print("Registering clearlogins scheduled task")
    register_clearlogins_task(ctx, ctx.config.aws, service_task_definition_arn)


@task(help={
    "mode": "Mode you want to deploy to: development, acceptance or production. Must match APPLICATION_MODE",
    "version": "Version of the project you want to deploy. Defaults to latest version"
})
def deploy(ctx, mode, version=None):
    """
    Updates the container cluster in development, acceptance or production environment on AWS to run a Docker image
    """
    target = ctx.config.project
    if target not in TARGETS:
        raise Exit(f"Unknown target: {target}", code=1)

    print(f"Starting deploy of {target}")

    target_info = TARGETS[target]
    version = version or target_info["version"]
    task_role_arn = ctx.config.aws.task_role_arn

    print(f"Starting AWS session for: {mode}")
    ecs_client = create_aws_session(ctx.config.aws.profile_name).client('ecs', )

    if target == "harvester":
        print(f"Deploying harvester version {version}")
        deploy_harvester(ctx, mode, ecs_client, task_role_arn, version)

    if target == "service":
        print(f"Deploying service version {version}")
        deploy_service(ctx, mode, ecs_client, task_role_arn, version)

    print("Done deploying")
