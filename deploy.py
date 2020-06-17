import os
import json

from invoke.tasks import task
from invoke.exceptions import Exit
from git import Repo
import boto3

from environments.surfpol import MODE, get_package_info
from service.package import (
    VERSION as SERVICE_VERSION,
    REPOSITORY as SERVICE_REPOSITORY,
    NAME as SERVICE_NAME
)
from harvester.package import VERSION as HARVESTER_VERSION


TARGETS = {
    "service": {  # TODO: perhaps simply input a PACKAGE from <target>/package.py which is a dict like below and work with that directly
        "name": SERVICE_NAME,
        "repository": SERVICE_REPOSITORY,
        "version": SERVICE_VERSION
    }
}


@task()
def prepare_builds(ctx):
    repo = Repo(".")
    commit = str(repo.head.commit)
    # TODO: we can make assertions about the git state like: no uncommited changes and no untracked files
    with open(os.path.join("portal", "package.json")) as portal_package_file:
        portal_package = json.load(portal_package_file)
    info = {
        "commit": commit,
        "versions": {
            "service": SERVICE_VERSION,
            "harvester": HARVESTER_VERSION,
            "portal": portal_package["version"]
        }
    }
    with open(os.path.join("environments", "info.json"), "w") as info_file:
        json.dump(info, info_file)


@task(prepare_builds)
def build(ctx, target, version):

    # Check the input for validity
    if target not in TARGETS:
        raise Exit(f"Unknown target: {target}", code=1)
    package_info = get_package_info()
    package_version = package_info["versions"][target]
    if package_version != version:
        raise Exit(
            f"Expected version of {target} to match {version} instead it's {package_version}. Update package.py?",
            code=1
        )

    # Gather necessary info and call Docker to build
    commit = package_info["commit"]  # TODO: Do we need the commit as a tag? Versions are more human readable
    target_info = TARGETS[target]
    ctx.run(
        f"docker build -f {target}/Dockerfile -t {target_info['name']}:{version} -t {target_info['name']}:{commit} .",
        pty=True,
        echo=True
    )


@task()
def push(ctx, target, version=None):

    # Check the input for validity
    if target not in TARGETS:
        raise Exit(f"Unknown target: {target}", code=1)
    # Load info
    target_info = TARGETS[target]
    version = version or target_info["version"]
    name = target_info["name"]
    repository = target_info["repository"]

    # Login with Docker to AWS
    ctx.run(
        "AWS_DEFAULT_PROFILE=pol-dev aws ecr get-login-password --region eu-central-1 | "
        f"docker login --username AWS --password-stdin {target_info['repository']}",
        echo=True
    )
    # Tag the image we want to push for AWS
    ctx.run(f"docker tag {name}:{version} {repository}/{name}:{version}", echo=True)
    # Push to AWS ECR
    ctx.run(f"docker push {repository}/{name}:{version}", echo=True, pty=True)


def register_task_definition(ecs_client, task_role_arn, target, mode, version):

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
    with open(os.path.join("service", "aws-container-definitions.json")) as container_definitions_file:
        container_definitions_json = container_definitions_file.read()
        container_variables = {
            "REPOSITORY": target_info["repository"],
            "NAME": target_info["name"],
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
        cpu="512",
        memory="1024",
        containerDefinitions=container_definitions
    )
    # And we update the service with new task definition
    task_definition = response["taskDefinition"]
    return target_info['name'], task_definition["taskDefinitionArn"]


@task()
def deploy(ctx, target, mode, version=None):

    # Setup the AWS SDK
    print(f"Starting AWS session for: {mode}")
    session = boto3.Session(profile_name=ctx.config.aws.profile_name)
    ecs_client = session.client('ecs', region_name='eu-central-1')

    target_name, task_definition_arn = register_task_definition(
        ecs_client,
        ctx.config.aws.task_role_arn,
        target,
        mode,
        version
    )

    print("Updating service")
    ecs_client.update_service(
        cluster=ctx.config.aws.cluster_arn,
        service=f"{target_name}",
        taskDefinition=task_definition_arn
    )


@task()
def migrate(ctx, target, mode, version=None):

    # Setup the AWS SDK
    print(f"Starting AWS session for: {mode}")
    session = boto3.Session(profile_name=ctx.config.aws.profile_name)
    ecs_client = session.client('ecs', region_name='eu-central-1')

    target_name, task_definition_arn = register_task_definition(
        ecs_client,
        ctx.config.aws.superuser_task_role_arn,
        target,
        mode,
        version
    )

    print("Migrating")
    ecs_client.run_task(
        cluster=ctx.config.aws.cluster_arn,
        taskDefinition=task_definition_arn,
        launchType="FARGATE",
        overrides={
            "containerOverrides": [{
                "name": "search-portal-container",
                "command": ["python", "manage.py", "migrate"],
                "environment": [
                    {
                        "name": "POL_DJANGO_POSTGRES_USER",
                        "value": f"{ctx.config.django.postgres_user}"
                    },
                    {
                        "name": "POL_SECRETS_POSTGRES_PASSWORD",
                        "value": f"{ctx.config.aws.postgres_password_arn}"
                    },
                ]
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
