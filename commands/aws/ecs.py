import json
from invoke import Exit

from environments.project import MODE, REPOSITORY, PROJECT
from commands.aws.utils import create_aws_session
from commands import TARGETS


TASK_CONTAINERS_BY_FAMILY = {
    "harvester": [
        "harvester-container",
        "flower-container",
    ],
    "harvester-command": [
        "harvester-container",
        "celery-worker-container",
        "analyzer",
    ],
    "celery": [
        "celery-worker-container",
        "celery-beat-container",
        "analyzer",
    ],
    "search-portal": [
        "search-portal-container",
    ]
}


def load_container_definitions(family, container_variables, is_public):
    print(f"Reading container definitions for: {family}")
    with open("aws-container-definitions.json") as container_definitions_file:
        container_definitions_json = container_definitions_file.read()
        for name, value in container_variables.items():
            container_definitions_json = container_definitions_json.replace(f"${{{name}}}", str(value))
        container_definitions = json.loads(container_definitions_json)
    containers = [container_definitions[container] for container in TASK_CONTAINERS_BY_FAMILY[family]]
    if is_public:
        containers.append(container_definitions[f"{family}-nginx"])
    return containers


def register_task_definition(family, ecs_client, task_role_arn, container_variables, is_public, cpu,
                             memory, extra_workers=False):
    # Read the service AWS container definition and replace some variables with actual values
    container_definitions = load_container_definitions(family, container_variables, is_public)
    # Now we push the task definition to AWS
    print("Setting up task definition")
    if extra_workers:
        print("Using more processors on larger machines")
        cpu_extra_workers = int(cpu)
        cpu_extra_workers *= 2
        cpu = str(cpu_extra_workers)
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


def run_task(ctx, target, mode, command, environment=None, version=None, extra_workers=False,
             is_harvester_command=False):
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
        "flower_secret_arn": ctx.config.aws.flower_secret_arn,
        "harvester_bucket": ctx.config.aws.harvest_content_bucket,
    })

    if extra_workers:
        container_variables.update({
            "concurrency": 4
        })

    task_definition_arn = register_task_definition(
        target_info["name"] if not is_harvester_command else "harvester-command",
        ecs_client,
        ctx.config.aws.superuser_task_role_arn,
        container_variables,
        False,
        target_info["cpu"],
        target_info["memory"],
        extra_workers
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
        "version": version,
        "project": PROJECT,
        "concurrency": 2  # matches amount of default CPU's
    }


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
