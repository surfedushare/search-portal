import os
import json
import boto3

from invoke.tasks import task
from invoke.exceptions import Exit
from git import Repo

from commands import TARGETS, REPOSITORY
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

    if target == 'service':
        ctx.run(
            f"docker build -f {target}/Dockerfile-nginx -t {target_info['name']}-nginx:{version} .",
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

    if target == 'service':
        ctx.run(f"docker tag {name}-nginx:{version} {REPOSITORY}/{name}-nginx:{version}", echo=True)
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
    session = boto3.Session(profile_name="pol-prod")
    ecr = session.client("ecr")

    # List images
    response = ecr.list_images(
        registryId="017973353230",
        repositoryName=name,
    )

    # Print output
    def image_version_sort(image):
        return tuple([int(section) for section in image["imageTag"].split(".")])
    images = sorted(response["imageIds"], key=image_version_sort, reverse=True)
    print(json.dumps(images[:10], indent=4))
