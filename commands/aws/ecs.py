import os
import json
from invoke import Exit

from environments.project import MODE
from commands.aws.utils import create_aws_session
from commands import TARGETS, REPOSITORY


def register_task_definition(family, ecs_client, task_role_arn, container_variables, container_definition_path, cpu,
                             memory):
    # Read the service AWS container definition and replace some variables with actual values
    print(f"Reading container definitions for: {family}")
    with open(container_definition_path) as container_definitions_file:
        container_definitions_json = container_definitions_file.read()
        for name, value in container_variables.items():
            container_definitions_json = container_definitions_json.replace(f"${{{name}}}", value)
        container_definitions = json.loads(container_definitions_json)

    # Now we push the task definition to AWS
    print("Setting up task definition")
    response = ecs_client.register_task_definition(
        family=family,
        taskRoleArn=task_role_arn,
        executionRoleArn=task_role_arn,
        networkMode="awsvpc",
        cpu=cpu,
        memory=memory,
        containerDefinitions=container_definitions
    )
    # And we update the service with new task definition
    task_definition = response["taskDefinition"]
    return task_definition["taskDefinitionArn"]


def run_task(ctx, target, mode, command, environment=None, version=None, extra_workers=False, concurrency=4):
    """
    Executes any (Django) command on container cluster for development, acceptance or production environment on AWS
    """
    if mode != MODE:
        raise Exit(f"Expected mode to match APPLICATION_MODE value but found: {mode}", code=1)

    environment = environment or []
    target_info = TARGETS[target]
    version = version or target_info["version"]

    # Setup the AWS SDK
    print(f"Starting AWS session for: {mode}")
    session = create_aws_session(profile_name=ctx.config.aws.profile_name)
    ecs_client = session.client('ecs')
    container_variables = build_default_container_variables(mode, version)
    container_variables.update({
        "harvester_bucket": ctx.config.aws.harvest_content_bucket
    })

    if extra_workers:
        container_variables.update({
            "concurrency": f"{concurrency}"
        })

    task_definition_arn = register_task_definition(
        target_info["name"],
        ecs_client,
        ctx.config.aws.superuser_task_role_arn,
        container_variables,
        os.path.join(target, task_container_definitions(target, extra_workers)),
        target_info["cpu"],
        target_info["memory"]
    )

    print(f"Target/mode/version: {target}/{mode}/{version}")
    print(f"Executing: {command}")
    ecs_client.run_task(
        cluster=ctx.config.aws.cluster_arn,
        taskDefinition=task_definition_arn,
        launchType="FARGATE",
        enableExecuteCommand=True,
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
                    ctx.config.aws.default_security_group_id,
                    ctx.config.aws.elasticsearch_security_group_id,
                    ctx.config.aws.redis_security_group_id
                ]
            }
        },
    )


def build_default_container_variables(mode, version):
    return {
        "REPOSITORY": REPOSITORY,
        "mode": mode,
        "version": version
    }


def task_container_definitions(target, extra_workers):
    if target == "service":
        return "aws-container-definitions.json"

    if extra_workers:
        return "task-with-workers-container-definitions.json"

    return "task-container-definitions.json"


def list_running_containers(ecs, cluster, service):
    tasks_response = ecs.list_tasks(
        cluster=cluster,
        serviceName=service,
        desiredStatus='RUNNING'
    )
    response = ecs.describe_tasks(
        cluster=cluster,
        tasks=tasks_response["taskArns"]
    )
    return [
        {
            "version": container["image"].split(":")[-1],
            "container_id": container.get("runtimeId", None)
        }
        for aws_task in response["tasks"] for container in aws_task["containers"] if service in container["name"]
    ]
