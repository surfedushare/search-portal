from time import sleep
from invoke import Exit, task
import boto3
from collections import defaultdict
from math import ceil

from environments.project import MODE
from commands import TARGETS


def get_private_network_configuration(aws_session):
    print("Acquiring subnet")
    ec2_client = aws_session.client('ec2')
    subnets_response = ec2_client.describe_subnets()
    vpc_id, private_subnet = next(
        ((subnet["VpcId"], subnet["SubnetId"],)
         for subnet in subnets_response["Subnets"] if not subnet["MapPublicIpOnLaunch"])
    )
    print("Acquiring security groups")
    security_groups_response = ec2_client.describe_security_groups(
        Filters=[
            {
                "Name": "vpc-id",
                "Values": [vpc_id]
            },
            {
                "Name": "group-name",
                "Values": ["default", "aws-services-access"]
            }
        ]
    )
    security_group_ids = [security_group["GroupId"] for security_group in security_groups_response["SecurityGroups"]]
    return {
        "awsvpcConfiguration": {
            "subnets": [private_subnet],
            "securityGroups": security_group_ids
        }
    }


def _get_superuser_command_override(superuser_task_role_arn, container, command, environment):
    return {
        "containerOverrides": [{
            "name": container,
            "command": command,
            "environment": environment
        }],
        "taskRoleArn": superuser_task_role_arn
    }


def run_task(ctx, target, mode, command, environment=None, extra_workers=False, is_harvester_command=False):
    """
    Executes any (Django) command on container cluster for development, acceptance or production environment on AWS
    """
    if mode != MODE:
        raise Exit(f"Expected mode to match APPLICATION_MODE value but found: {mode}", code=1)

    environment = environment or []
    target_info = TARGETS[target]

    # Setup the AWS SDK
    print(f"Starting AWS session for: {mode}")
    session = boto3.Session(profile_name=ctx.config.aws.profile_name, region_name="eu-central-1")
    ecs_client = session.client('ecs')

    # Building overrides configuration
    cpu = int(target_info["cpu"])
    overrides = _get_superuser_command_override(
        ctx.config.aws.superuser_task_role_arn,
        f"{target_info['name']}-container",
        command,
        environment
    )
    if extra_workers:
        overrides["cpu"] = str(cpu*2)

    print(f"Target/mode: {target}/{mode}")
    print(f"Executing: {command}")
    ecs_client.run_task(
        cluster=ctx.config.aws.cluster_name,
        taskDefinition=target_info["name"] if not is_harvester_command else "harvester-command",
        launchType="FARGATE",
        enableExecuteCommand=True,
        overrides=overrides,
        networkConfiguration=get_private_network_configuration(session)
    )


def run_data_engineering_task(ctx, target, mode, command, environment=None):
    """
    Executes any (Django) command on (data engineering) cluster for development, acceptance or production environment
    """
    if mode != MODE:
        raise Exit(f"Expected mode to match APPLICATION_MODE value but found: {mode}", code=1)

    environment = environment or []

    # Setup the AWS SDK
    print(f"Starting AWS session for: {mode}")
    session = boto3.Session(profile_name=ctx.config.aws.profile_name, region_name="eu-central-1")
    ecs_client = session.client('ecs')

    print(f"Target/mode: {target}/{mode}")
    print(f"Executing: {command}")
    superuser_task_role = ctx.config.aws.superuser_task_role_arn
    ecs_client.run_task(
        cluster=ctx.config.aws.cluster_name,
        taskDefinition=f"command-{target}",
        launchType="FARGATE",
        overrides=_get_superuser_command_override(superuser_task_role, f"command-{target}", command, environment),
        networkConfiguration=get_private_network_configuration(session)
    )


def _cleanup_ecs_task_registrations(ctx, ecs_client):
    next_token = None
    families = iter(ctx.config.aws.task_definition_families)
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
                    if ctx.config.aws.environment_code in container["image"].split("/")[1]
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
    production_account = ctx.config.aws.production.account
    environments = ["prod", "acc", "dev"]
    images = {
        repository: defaultdict(list)
        for repository in ctx.config.aws.repositories
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
                is_promoted = next((env for env in environments if env in tag and len(tag) < 40), False)
                if is_promoted:
                    print("Skipping delete of image digest for environment:", tag)
                    break
                elif "." in tag:
                    raw_version = tag.split(".")
                    major_minor_version = float(".".join(raw_version[:2]))
                    if major_minor_version > version_cutoff:
                        print("Skipping delete of image digest with version:", tag)
                        break
            else:
                print("Deleting image digest:", digest)
                delete_digests.append({"imageDigest": digest})
        for offset in range(ceil(len(delete_digests)/100)):
            ecr_client.batch_delete_image(
                registryId=production_account,
                repositoryName=repository,
                imageIds=list(delete_digests[offset:offset+100])
            )
            sleep(1)


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
    if ctx.config.service.env == "production":
        ecr_client = session.client('ecr')
        _cleanup_ecr_images(ctx, ecr_client, version_cutoff)
