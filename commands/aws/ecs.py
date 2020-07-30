import os
import json
from invoke import Exit
import boto3

from commands import TARGETS, REPOSITORY
from environments.surfpol import MODE


def register_task_definition(ecs_client, task_role_arn, target, mode, version, cpu, memory):

    # Validating input
    if target not in TARGETS:
        raise Exit(f"Unknown target: {target}", code=1)
    if mode != MODE:
        raise Exit(f"Expected mode to match APPLICATION_MODE value but found: {mode}", code=1)

    # Load data
    target_info = TARGETS[target]
    version = version or target_info["version"]

    # Read the service AWS container definition and replace some variables with actual values
    print(f"Reading container definitions for: {target_info['name']}")
    with open(os.path.join(target, "aws-container-definitions.json")) as container_definitions_file:
        container_definitions_json = container_definitions_file.read()
        container_variables = {
            "REPOSITORY": REPOSITORY,
            "mode": mode,
            "version": version
        }
        for name, value in container_variables.items():
            container_definitions_json = container_definitions_json.replace(f"${{{name}}}", value)
        container_definitions = json.loads(container_definitions_json)

    # Now we push the task definition to AWS
    print("Setting up task definition")
    response = ecs_client.register_task_definition(
        family=f"{target_info['name']}",
        taskRoleArn=task_role_arn,
        executionRoleArn=task_role_arn,
        networkMode="awsvpc",
        cpu=cpu,
        memory=memory,
        containerDefinitions=container_definitions
    )
    # And we update the service with new task definition
    task_definition = response["taskDefinition"]
    return target_info['name'], task_definition["taskDefinitionArn"]


def run_task(ctx, target, mode, command, environment=None, version=None):
    """
    Executes any (Django) command on container cluster for development, acceptance or production environment on AWS
    """
    if mode != MODE:
        raise Exit(f"Expected mode to match APPLICATION_MODE value but found: {mode}", code=1)

    environment = environment or []

    # Setup the AWS SDK
    print(f"Starting AWS session for: {mode}")
    session = boto3.Session(profile_name=ctx.config.aws.profile_name)
    ecs_client = session.client('ecs', region_name='eu-central-1')

    target_info = TARGETS[target]
    target_name, task_definition_arn = register_task_definition(
        ecs_client,
        ctx.config.aws.superuser_task_role_arn,
        target,
        mode,
        version,
        target_info["cpu"],
        target_info["memory"]
    )

    print(f"Target/mode: {target}/{mode}")
    print(f"Executing: {command}")
    ecs_client.run_task(
        cluster=ctx.config.aws.cluster_arn,
        taskDefinition=task_definition_arn,
        launchType="FARGATE",
        overrides={
            "containerOverrides": [{
                "name": f"{target_info['name']}-container",
                "command": command,
                "environment": environment
            }]
        },
        networkConfiguration={
            "awsvpcConfiguration": {
                "subnets": [ctx.config.aws.private_subnet_id],
                "securityGroups": [
                    ctx.config.aws.rds_security_group_id,
                    ctx.config.aws.default_security_group_id

                ]
            }
        },
    )
