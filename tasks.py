import os
import json

from invoke import Collection
from invoke.tasks import task
from invoke.exceptions import Exit
from git import Repo
import boto3

from environments.surfpol import environment, MODE, get_package_info
from elastic.tasks import setup, create_snapshot, load_repository, restore_snapshot

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
        "aws ecr get-login-password --region eu-central-1 | "
        f"docker login --username AWS --password-stdin {target_info['repository']}",
        echo=True
    )
    # Tag the image we want to push for AWS
    ctx.run(f"docker tag {name}:{version} {repository}/{name}:{version}", echo=True)
    # Push to AWS ECR
    ctx.run(f"docker push {repository}/{name}:{version}", echo=True, pty=True)


@task()
def deploy(ctx, target, mode, version=None):

    # Check the input for validity
    if target not in TARGETS:
        raise Exit(f"Unknown target: {target}", code=1)
    if mode != MODE:
        raise Exit(f"Expected mode to match APPLICATION_MODE value but found: {mode}", code=1)
    # Load info
    target_info = TARGETS[target]
    version = version or target_info["version"]

    # Read the service AWS container definition and replace some variables with actual values
    print(f"Reading container definitions for: {target_info['name']}")
    with open(os.path.join("service", "aws-container-definitions.json")) as container_definitions_file:  # TODO: strip all "dev" from container definition
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

    # Setup the AWS SDK
    print(f"Starting AWS session for: {mode}")
    session = boto3.Session(profile_name=ctx.config.aws.profile_name)
    client = session.client('ecs', region_name='eu-central-1')
    # Now we push the task definition to AWS
    print("Setting up task definition")
    task_role_arn = ctx.config.aws.task_role_arn
    response = client.register_task_definition(
        family=f"{target_info['name']}-dev",  # TODO: strip the dev postfix
        taskRoleArn=task_role_arn,
        executionRoleArn=task_role_arn,
        networkMode="awsvpc",
        cpu="512",
        memory="1024",
        containerDefinitions=container_definitions
    )
    # And we update the service with new task definition
    print("Updating service")
    task_definition = response["taskDefinition"]
    task_definition_arn = task_definition["taskDefinitionArn"]
    client.update_service(
        cluster=ctx.config.aws.cluster_arn,
        service=f"{target_info['name']}-dev",  # TODO: strip postfix
        taskDefinition=task_definition_arn
    )


namespace = Collection(
    Collection("es", setup, create_snapshot, load_repository, restore_snapshot),
    prepare_builds,
    build,
    push,
    deploy
)
namespace.configure(environment)
