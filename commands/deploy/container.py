import os
import json
import boto3

from invoke.tasks import task
from invoke.exceptions import Exit
from git import Repo

from commands import TARGETS
from environments.project import REPOSITORY, REPOSITORY_AWS_PROFILE


def get_commit_hash():
    repo = Repo(".")
    return str(repo.head.commit)


@task(help={
    "commit": "The commit hash a new build should include in its info.json"
})
def prepare_builds(ctx, commit=None):
    """
    Makes sure that repo information will be present inside Docker images
    """
    commit = commit or get_commit_hash()

    service_package = TARGETS["service"]
    harvester_package = TARGETS["harvester"]
    info = {
        "commit": commit,
        "versions": {
            "service": service_package["version"],
            "harvester": harvester_package["version"]
        }
    }
    with open(os.path.join("environments", "info.json"), "w") as info_file:
        json.dump(info, info_file)


@task(help={
    "target": "Name of the project you want to build: service or harvester",
    "commit": "The commit hash a new build should include in its info.json. Will also be used to tag the new image."
})
def build(ctx, target, commit=None):
    """
    Uses Docker to build an image for a Django project
    """
    commit = commit or get_commit_hash()

    prepare_builds(ctx, commit)

    # Check the input for validity
    if target not in TARGETS:
        raise Exit(f"Unknown target: {target}", code=1)

    # Gather necessary info and call Docker to build
    target_info = TARGETS[target]
    ctx.run(
        f"docker build -f {target}/Dockerfile -t {target_info['name']}:{commit} .",
        pty=True,
        echo=True
    )
    ctx.run(
        f"docker build -f nginx/Dockerfile-nginx -t {target_info['name']}-nginx:{commit} .",
        pty=True,
        echo=True
    )


@task(help={
    "target": "Name of the project you want to push to AWS registry: service or harvester",
    "commit": "The commit hash that the image to be pushed is tagged with."
})
def push(ctx, target, commit=None, docker_login=False):
    """
    Pushes a previously made Docker image to the AWS container registry, that's shared between environments
    """
    commit = commit or get_commit_hash()

    # Check the input for validity
    if target not in TARGETS:
        raise Exit(f"Unknown target: {target}", code=1)
    # Load info
    target_info = TARGETS[target]
    name = target_info["name"]

    # Login with Docker on AWS
    if docker_login:
        ctx.run(
            f"AWS_PROFILE={REPOSITORY_AWS_PROFILE} aws ecr get-login-password --region eu-central-1 | "
            f"docker login --username AWS --password-stdin {REPOSITORY}",
            echo=True
        )

    # Check if version tag already exists in registry
    inspection = ctx.run(f"docker manifest inspect {REPOSITORY}/{name}:{commit}", warn=True)
    if inspection.exited == 0:
        raise Exit("Can't push for commit that already has an image in the registry")

    # Tagging and pushing of our image and nginx image
    ctx.run(f"docker tag {name}:{commit} {REPOSITORY}/{name}:{commit}", echo=True)
    ctx.run(f"docker push {REPOSITORY}/{name}:{commit}", echo=True, pty=True)
    ctx.run(f"docker tag {name}-nginx:{commit} {REPOSITORY}/{name}-nginx:{commit}", echo=True)
    ctx.run(f"docker push {REPOSITORY}/{name}-nginx:{commit}", echo=True, pty=True)


@task(help={
    "target": "Name of the project you want to promote: service or harvester",
    "commit": "The commit hash that the image to be promoted is tagged with"
})
def promote(ctx, target, commit=None, docker_login=False):
    """
    Pushes a previously made Docker image to the AWS container registry, that's shared between environments
    """
    commit = commit or get_commit_hash()

    # Check the input for validity
    if target not in TARGETS:
        raise Exit(f"Unknown target: {target}", code=1)
    # Load info
    target_info = TARGETS[target]
    name = target_info["name"]
    version = target_info["version"]

    # Login with Docker on AWS
    if docker_login:
        ctx.run(
            f"AWS_PROFILE={REPOSITORY_AWS_PROFILE} aws ecr get-login-password --region eu-central-1 | "
            f"docker login --username AWS --password-stdin {REPOSITORY}",
            echo=True
        )

    # Check if version tag already exists in registry
    inspection = ctx.run(f"docker manifest inspect {REPOSITORY}/{name}:{version}", warn=True)
    if inspection.exited == 0:
        raise Exit(f"Can't promote commit to {version}, because that version tag already exists")

    # Pulling the relevant images
    ctx.run(f"docker pull {REPOSITORY}/{name}:{commit}", echo=True, pty=True)
    ctx.run(f"docker pull {REPOSITORY}/{name}-nginx:{commit}", echo=True, pty=True)

    # Tagging and pushing of our image and nginx image with version number from package files
    ctx.run(f"docker tag {REPOSITORY}/{name}:{commit} {REPOSITORY}/{name}:{version}", echo=True)
    ctx.run(f"docker push {REPOSITORY}/{name}:{version}", echo=True, pty=True)
    ctx.run(f"docker tag {REPOSITORY}/{name}-nginx:{commit} {REPOSITORY}/{name}-nginx:{version}", echo=True)
    ctx.run(f"docker push {REPOSITORY}/{name}-nginx:{version}", echo=True, pty=True)


@task(help={
    "target": "Name of the project you want to list images for: service or harvester",
})
def print_available_images(ctx, target):
    # Check the input for validity
    if target not in TARGETS:
        raise Exit(f"Unknown target: {target}", code=1)

    # Load info
    target_info = TARGETS[target]
    name = target_info["name"]

    # Start boto
    session = boto3.Session(profile_name=f"{ctx.config.project.prefix}-prod")
    ecr = session.client("ecr")

    # List images
    production_account = "017973353230" if ctx.config.project.prefix != "nppo" else "870512711545"
    response = ecr.list_images(
        registryId=production_account,
        repositoryName=name,
    )

    # Print output
    def image_version_sort(image):
        return tuple([int(section) for section in image["imageTag"].split(".")])
    images = [image for image in response["imageIds"] if "." in image["imageTag"]]
    images.sort(key=image_version_sort, reverse=True)
    print(json.dumps(images[:10], indent=4))
