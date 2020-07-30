import os
import json

from invoke.tasks import task
from invoke.exceptions import Exit
from git import Repo
import boto3

from commands import TARGETS, REPOSITORY
from commands.aws.ecs import register_task_definition, run_task
from environments.surfpol import get_package_info


@task()
def prepare_builds(ctx):
    """
    Makes sure that repo information will be present inside Docker images
    """
    repo = Repo(".")
    commit = str(repo.head.commit)
    # TODO: we can make assertions about the git state like: no uncommited changes and no untracked files
    with open(os.path.join("portal", "package.json")) as portal_package_file:
        portal_package = json.load(portal_package_file)
    service_package = TARGETS["service"]
    harvester_package = TARGETS["harvester"]
    info = {
        "commit": commit,
        "versions": {
            "service": service_package["version"],
            "harvester": harvester_package["version"],
            "portal": portal_package["version"]
        }
    }
    with open(os.path.join("environments", "info.json"), "w") as info_file:
        json.dump(info, info_file)


@task(prepare_builds, help={
    "target": "Name of the project you want to build: service or harvester",
    "version": "Version of the project you want to build. Must match value in package.py"
})
def build(ctx, target, version):
    """
    Uses Docker to build an image for a Django project
    """

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
    target_info = TARGETS[target]
    ctx.run(
        f"docker build -f {target}/Dockerfile -t {target_info['name']}:{version} .",
        pty=True,
        echo=True
    )


@task(help={
    "target": "Name of the project you want to push to AWS registry: service or harvester",
    "version": "Version of the project you want to push. Defaults to latest version"
})
def push(ctx, target, version=None):
    """
    Pushes a previously made Docker image to the AWS container registry, that's shared between environments
    """

    # Check the input for validity
    if target not in TARGETS:
        raise Exit(f"Unknown target: {target}", code=1)
    # Load info
    target_info = TARGETS[target]
    version = version or target_info["version"]
    name = target_info["name"]

    # Login with Docker to AWS
    ctx.run(
        "AWS_PROFILE=pol-prod aws ecr get-login-password --region eu-central-1 | "
        f"docker login --username AWS --password-stdin {REPOSITORY}",
        echo=True
    )
    # Tag the image we want to push for AWS
    ctx.run(f"docker tag {name}:{version} {REPOSITORY}/{name}:{version}", echo=True)
    # Push to AWS ECR
    ctx.run(f"docker push {REPOSITORY}/{name}:{version}", echo=True, pty=True)


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


@task(help={
    "target": "Name of the project you want migrate on AWS: service or harvester",
    "mode": "Mode you want to migrate: development, acceptance or production. Must match APPLICATION_MODE",
    "version": "Version of the project you want to migrate. Defaults to latest version"
})
def migrate(ctx, target, mode, version=None):
    """
    Executes migration task on container cluster for development, acceptance or production environment on AWS
    """
    command = ["python", "manage.py", "migrate"]
    environment = [
        {
            "name": "POL_DJANGO_POSTGRES_USER",
            "value": f"{ctx.config.django.postgres_user}"
        },
        {
            "name": "POL_SECRETS_POSTGRES_PASSWORD",
            "value": f"{ctx.config.aws.postgres_password_arn}"
        },
    ]
    run_task(ctx, target, mode, command, environment, version=version)
