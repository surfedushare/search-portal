import json
from time import sleep
from invoke import Exit, task
import boto3
from collections import defaultdict
from math import ceil

from environments.project import MODE, REPOSITORY, PROJECT, FARGATE_CLUSTER_NAME
from commands import TARGETS
from commands.aws import ENVIRONMENT_NAMES_TO_CODES


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


def _register_run_task_definition(ctx, ecs_client, target_info, mode, version=None, extra_workers=False,
                                  is_harvester_command=False):

    container_variables = build_default_container_variables(mode, version)
    container_variables.update({
        "flower_secret_arn": ctx.config.aws.flower_secret_arn,
        "harvester_bucket": ctx.config.aws.harvest_content_bucket,
    })

    if extra_workers:
        container_variables.update({
            "concurrency": 4
        })

    return register_task_definition(
        target_info["name"] if not is_harvester_command else "harvester-command",
        ecs_client,
        ctx.config.aws.superuser_task_role_arn,
        container_variables,
        False,
        target_info["cpu"],
        target_info["memory"],
        extra_workers
    )


def run_task(ctx, target, mode, command, environment=None, version=None, extra_workers=False,
             is_harvester_command=False, legacy_system=True):
    """
    Executes any (Django) command on container cluster for development, acceptance or production environment on AWS
    """
    if mode != MODE:
        raise Exit(f"Expected mode to match APPLICATION_MODE value but found: {mode}", code=1)
    if not legacy_system and version:
        raise Exit("Can't run a command with a specific version. Use the promote command to switch between versions.")

    environment = environment or []
    target_info = TARGETS[target]
    version = version or target_info["version"]

    # Setup the AWS SDK
    print(f"Starting AWS session for: {mode}")
    session = boto3.Session(profile_name=ctx.config.aws.profile_name, region_name="eu-central-1")
    ecs_client = session.client('ecs')

    # Switch between legacy and new deploy system
    if legacy_system:
        print("Legacy run with version:", version)
        task_definition = _register_run_task_definition(
            ctx, ecs_client, target_info, mode, version, extra_workers, is_harvester_command
        )
    else:
        task_definition = target_info["name"] if not is_harvester_command else "harvester-command"

    # Building overrides configuration
    cpu = int(target_info["cpu"])
    overrides = {
        "containerOverrides": [{
            "name": f"{target_info['name']}-container",
            "command": command,
            "environment": environment
        }],
        "taskRoleArn": ctx.config.aws.superuser_task_role_arn,
    }
    if extra_workers:
        overrides["cpu"] = str(cpu*2)

    print("Acquiring subnet")
    ec2_client = session.client('ec2')
    subnets_response = ec2_client.describe_subnets()
    private_subnet = next(
        (subnet["SubnetId"] for subnet in subnets_response["Subnets"] if not subnet["MapPublicIpOnLaunch"])
    )

    print(f"Target/mode: {target}/{mode}")
    print(f"Executing: {command}")
    ecs_client.run_task(
        cluster=FARGATE_CLUSTER_NAME,
        taskDefinition=task_definition,
        launchType="FARGATE",
        enableExecuteCommand=True,
        overrides=overrides,
        networkConfiguration={
            "awsvpcConfiguration": {
                "subnets": [private_subnet],
                "securityGroups": [
                    ctx.config.aws.rds_security_group_id,
                    ctx.config.aws.default_security_group_id,
                    ctx.config.aws.opensearch_security_group_id,
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


def _cleanup_ecs_task_registrations(ctx, ecs_client):
    next_token = None
    families = iter(["harvester", "search-portal", "celery", "harvester-command"])
    family = next(families)
    print("Starting cleanup of task registrations for:", family)
    while True:
        # Make request to AWS
        kwargs = {
            "familyPrefix": family,
            "status": "ACTIVE",
            "sort": "DESC",
            "maxResults": 100,
        }
        if next_token:
            kwargs["nextToken"] = next_token
        task_definitions_response = ecs_client.list_task_definitions(**kwargs)
        # Process info from response
        for task_definition_arn in task_definitions_response["taskDefinitionArns"]:
            task_definition_details = ecs_client.describe_task_definition(taskDefinition=task_definition_arn)
            is_valid_task_definition = next(
                (
                    container for container in task_definition_details["taskDefinition"]["containerDefinitions"]
                    if container["image"].endswith(ENVIRONMENT_NAMES_TO_CODES[ctx.config.env])
                ),
                False
            )
            if not is_valid_task_definition:
                print("Deregistering:", task_definition_arn)
                ecs_client.deregister_task_definition(taskDefinition=task_definition_arn)
                sleep(1)
        # Prepare next request
        next_token = task_definitions_response.get("nextToken", None)
        if not next_token:
            family = next(families, None)
            if not family:
                break
            print("Starting cleanup of task registrations for:", family)


def _cleanup_ecr_images(ctx, ecr_client, version_cutoff):
    next_token = None
    production_account = "322480324822" if ctx.config.project.prefix != "nppo" else "870512711545"
    environments = ENVIRONMENT_NAMES_TO_CODES.values()
    images = {
        repository: defaultdict(list)
        for repository in ["harvester", "harvester-nginx", "search-portal", "search-portal-nginx"]
    }
    repositories = iter(images.keys())
    repository = next(repositories)
    print("Starting cleanup of repository:", repository)
    while True:
        # Make request to AWS
        kwargs = {
            "registryId": production_account,
            "repositoryName": repository
        }
        if next_token:
            kwargs["nextToken"] = next_token
        list_images_response = ecr_client.list_images(**kwargs)
        # Process info from response
        for image_info in list_images_response["imageIds"]:
            tag = image_info.get("imageTag", None)
            if not tag:
                images[repository][image_info["imageDigest"]] = []
                continue
            images[repository][image_info["imageDigest"]].append(tag)
        # Prepare next request
        next_token = list_images_response.get("nextToken", None)
        if not next_token:
            repository = next(repositories, None)
            if not repository:
                break
            print("Starting cleanup of repository:", repository)
    # Actual delete of images
    for repository, repository_images in images.items():
        print("Deleting images for:", repository)
        delete_digests = []
        for digest, tags in repository_images.items():
            if len(tags) < 2:  # any old images or images without version tags may be deleted
                print("Deleting obsolete image digest:", digest)
                delete_digests.append({"imageDigest": digest})
                continue
            if not version_cutoff:  # all other images remain unless a version_cutoff has been specified
                continue
            for tag in tags:
                if tag in environments:  # always skip any promoted images
                    print("Skipping delete of image digest for environment:", tag)
                    break
                elif "." in tag:
                    raw_version = tag.split(".")
                    major_minor_version = float(".".join(raw_version[:2]))
                    if major_minor_version < version_cutoff:
                        print("Deleting image digest with version:", tag)
            else:
                delete_digests.append({"imageDigest": digest})
        for offset in range(ceil(len(delete_digests)/100)):
            ecr_client.batch_delete_image(
                registryId=production_account,
                repositoryName=repository,
                imageIds=list(delete_digests[offset:offset+100])
            )


@task(help={
    "mode": "Mode you want to clean artifacts for: development, acceptance or production. Must match APPLICATION_MODE",
    "version_cutoff": "When specified any images with versions below this major and minor version will get deleted",
})
def cleanup_ecs_artifacts(ctx, mode, version_cutoff=None):
    if version_cutoff:
        version_cutoff = float(version_cutoff)
    # Setup the AWS SDK
    print(f"Starting AWS session for: {mode}")
    session = boto3.Session(profile_name=ctx.config.aws.profile_name, region_name="eu-central-1")
    ecs_client = session.client('ecs')
    _cleanup_ecs_task_registrations(ctx, ecs_client)
    if ctx.config.env == "production":
        ecr_client = boto3.client('ecr')
        _cleanup_ecr_images(ctx, ecr_client, version_cutoff)
