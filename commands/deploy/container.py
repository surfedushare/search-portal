import os
import json
import boto3

from invoke.tasks import task
from invoke.exceptions import Exit
from git import Repo

from commands import TARGETS
from environments.project import REPOSITORY


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
    "docker_login": "Specify this flag to login to AWS registry. Needed only once per session"
})
def publish_runner_image(ctx, docker_login=False):
    """
    Uses Docker to build and push an image to use as Gitlab pipeline image
    """

    ctx.run("docker build -f Dockerfile-runner -t gitlab-runner .", pty=True, echo=True)

    # Login with Docker on AWS
    if docker_login:
        ctx.run(
            f"aws ecr get-login-password --region eu-central-1 | "
            f"docker login --username AWS --password-stdin {REPOSITORY}",
            echo=True
        )

    ctx.run(f"docker tag gitlab-runner:latest {REPOSITORY}/gitlab-runner:latest", echo=True)
    ctx.run(f"docker push {REPOSITORY}/gitlab-runner:latest", echo=True, pty=True)


@task(help={
    "target": "Name of the project you want to build: service or harvester",
    "commit": "The commit hash a new build should include in its info.json. Will also be used to tag the new image.",
    "docker_login": "Specify this flag to login to AWS registry. Needed only once per session"
})
def build(ctx, target, commit=None, docker_login=False):
    """
    Uses Docker to build an image for a Django project
    """
    commit = commit or get_commit_hash()

    prepare_builds(ctx, commit)

    # Check the input for validity
    if target not in TARGETS:
        raise Exit(f"Unknown target: {target}", code=1)

    # Login with Docker on AWS
    if docker_login:
        ctx.run(
            f"aws ecr get-login-password --region eu-central-1 | "
            f"docker login --username AWS --password-stdin {REPOSITORY}",
            echo=True
        )

    # Gather necessary info and call Docker to build
    target_info = TARGETS[target]
    name = target_info['name']
    latest_remote_image = f"{REPOSITORY}/{name}:latest"
    ctx.run(
        f"DOCKER_BUILDKIT=1 docker build "
        f"--build-arg BUILDKIT_INLINE_CACHE=1 --cache-from {latest_remote_image} --progress=plain "
        f"-f {target}/Dockerfile -t {name}:{commit} .",
        pty=True,
        echo=True
    )
    ctx.run(
        f"docker build -f nginx/Dockerfile-nginx -t {name}-nginx:{commit} .",
        pty=True,
        echo=True
    )


@task(help={
    "target": "Name of the project you want to push to AWS registry: service or harvester",
    "commit": "The commit hash that the image to be pushed is tagged with.",
    "docker_login": "Specify this flag to login to AWS registry. Needed only once per session",
    "push_latest": "Makes the command push a latest tag to use these layers later."
})
def push(ctx, target, commit=None, docker_login=False, push_latest=False):
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
            f"aws ecr get-login-password --region eu-central-1 | "
            f"docker login --username AWS --password-stdin {REPOSITORY}",
            echo=True
        )

    # Check if version tag already exists in registry
    inspection = ctx.run(f"docker manifest inspect {REPOSITORY}/{name}:{commit}", warn=True)
    if inspection.exited == 0:
        raise Exit("Can't push for commit that already has an image in the registry")

    # Tagging and pushing of our image and nginx image
    tags = [commit]
    if push_latest:
        tags.append("latest")
    for tag in tags:
        ctx.run(f"docker tag {name}:{commit} {REPOSITORY}/{name}:{tag}", echo=True)
        ctx.run(f"docker push {REPOSITORY}/{name}:{tag}", echo=True, pty=True)
        ctx.run(f"docker tag {name}-nginx:{commit} {REPOSITORY}/{name}-nginx:{tag}", echo=True)
        ctx.run(f"docker push {REPOSITORY}/{name}-nginx:{tag}", echo=True, pty=True)


@task(help={
    "target": "Name of the project you want to promote: service or harvester",
    "commit": "The commit hash that the image to be promoted is tagged with",
    "docker_login": "Specify this flag to login to AWS registry. Needed only once per session"
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
            f"aws ecr get-login-password --region eu-central-1 | "
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
