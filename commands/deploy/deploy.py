import json

from invoke.tasks import task
from invoke.exceptions import Exit
import boto3

from commands import TARGETS
from commands.aws.ecs import register_task_definition


def register_clearlogins_task(session, aws_config, task_definition_arn):
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


@task(help={
    "target": "Name of the project you want to deploy on AWS: service or harvester",
    "mode": "Mode you want to deploy to: development, acceptance or production. Must match APPLICATION_MODE",
    "version": "Version of the project you want to deploy. Defaults to latest version"
})
def deploy(ctx, target, mode, version=None):
    """
    Updates the container cluster in development, acceptance or production environment on AWS to run a Docker image
    """
    if target not in TARGETS:
        raise Exit(f"Unknown target: {target}", code=1)
    target_info = TARGETS[target]

    # Setup the AWS SDK
    print(f"Starting AWS session for: {mode}")
    session = boto3.Session(profile_name=ctx.config.aws.profile_name, region_name='eu-central-1')
    ecs_client = session.client('ecs', )
    task_role_arn = ctx.config.aws.harvester_task_role_arn if target == "harvester" else \
        ctx.config.aws.task_role_arn

    target_name, task_definition_arn = register_task_definition(
        ecs_client,
        task_role_arn,
        target,
        mode,
        version,
        target_info["cpu"],
        target_info["memory"]
    )

    print("Updating service")
    ecs_client.update_service(
        cluster=ctx.config.aws.cluster_arn,
        service=f"{target_name}",
        taskDefinition=task_definition_arn
    )

    if target == "service":
        print("Registering clearlogins scheduled task")
        register_clearlogins_task(session, ctx.config.aws, task_definition_arn)

    print("Done deploying")