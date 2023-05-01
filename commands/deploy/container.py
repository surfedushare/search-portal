import os
import json
import boto3

from invoke.tasks import task
from invoke.exceptions import Exit
from git import Repo

from commands import TARGETS


def get_commit_hash():
    repo = Repo(".")
    return str(repo.head.commit)


def aws_docker_login(ctx):
    command = f"aws ecr get-login-password --region eu-central-1 | " \
              f"docker login --username AWS --password-stdin {ctx.config.aws.production.registry}"
    if os.environ.get("AWS_PROFILE", None):
        command = f"AWS_PROFILE={ctx.config.aws.production.profile_name} " + command
        ctx.run(command)
    ctx.run(command, echo=True)


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

    ctx.run("docker build --platform=linux/amd64 -f Dockerfile-runner -t gitlab-runner .", pty=True, echo=True)

    # Login with Docker on AWS
    if docker_login:
        aws_docker_login(ctx)

    ctx.run(f"docker tag gitlab-runner:latest {ctx.config.aws.production.registry}/gitlab-runner:latest", echo=True)
    ctx.run(f"docker push {ctx.config.aws.production.registry}/gitlab-runner:latest", echo=True, pty=True)


@task(help={
    "docker_login": "Specify this flag to login to AWS registry. Needed only once per session"
})
def publish_tika_image(ctx, docker_login=False):
    """
    Uses Docker to build and push an image to use as tika image with configuration
    """

    ctx.run("docker build --platform=linux/amd64 -f tika/Dockerfile-tika -t harvester-tika .", pty=True, echo=True)

    # Login with Docker on AWS
    if docker_login:
        aws_docker_login(ctx)

    ctx.run(f"docker tag harvester-tika:latest {ctx.config.aws.production.registry}/harvester-tika:latest", echo=True)
    ctx.run(f"docker push {ctx.config.aws.production.registry}/harvester-tika:latest", echo=True, pty=True)


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
        aws_docker_login(ctx)

    # Gather necessary info and call Docker to build
    target_info = TARGETS[target]
    name = target_info['name']
    # TODO: remove later: latest_remote_image = f"{REPOSITORY}/{name}:latest"
    ctx.run(
        f"docker build "
        f"--progress=plain "
        f"--platform=linux/amd64 -f {target}/Dockerfile -t {name}:{commit} .",
        pty=True,
        echo=True
    )
    ctx.run(
        f"docker build --platform=linux/amd64 -f nginx/Dockerfile-nginx -t {name}-nginx:{commit} .",
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
    registry = ctx.config.aws.production.registry

    # Check the input for validity
    if target not in TARGETS:
        raise Exit(f"Unknown target: {target}", code=1)
    # Load info
    target_info = TARGETS[target]
    name = target_info["name"]

    # Login with Docker on AWS
    if docker_login:
        aws_docker_login(ctx)

    # Check if commit tag already exists in registry
    push_commit_tag = True
    inspection = ctx.run(f"docker manifest inspect {registry}/{name}:{commit}", warn=True)
    if inspection.exited == 0:
        print("Can't push commit tag that already has an image in the registry. Skipping.")
        push_commit_tag = False

    # Tagging and pushing of our image and nginx image
    tags = [commit] if push_commit_tag else []
    if push_latest:
        tags.append("latest")
    for tag in tags:
        ctx.run(f"docker tag {name}:{commit} {registry}/{name}:{tag}", echo=True)
        ctx.run(f"docker push {registry}/{name}:{tag}", echo=True, pty=True)
        ctx.run(f"docker tag {name}-nginx:{commit} {registry}/{name}-nginx:{tag}", echo=True)
        ctx.run(f"docker push {registry}/{name}-nginx:{tag}", echo=True, pty=True)


@task(
    help={
        "target": "Name of the project you want to promote: service or harvester",
        "commit": "The commit hash that the image to be promoted is tagged with",
        "docker_login": "Specify this flag to login to AWS registry. Needed only once per session",
        "version": "Which version to promote. Defaults to version specified in package.py.",
        "exclude": "List deploy targets that you want to exclude from this deploy like: "
                   "edusources, publinova or central",
    },
    iterable=["exclude"]
)
def promote(ctx, target, commit=None, docker_login=False, version=None, exclude=None):
    """
    Pushes a previously made Docker image to the AWS container registry, that's shared between environments
    """
    # Check the input for validity
    if target not in TARGETS:
        raise Exit(f"Unknown target: {target}", code=1)
    if commit and version:
        raise Exit("Can't promote a version and commit at the same time.")
    if ctx.config.service.env == "localhost":
        raise Exit("Can't promote for localhost environment")

    # Load info variables
    target_info = TARGETS[target]
    name = target_info["name"]
    commit = commit or get_commit_hash()
    is_version_promotion = bool(version)

    # Prepare promote
    registry = ctx.config.aws.production.registry
    version = version or target_info["version"]
    deploy_tags = dict(**ctx.config.service.deploy.tags)
    for exclusion in exclude:
        deploy_tags.pop(exclusion, None)
    if not deploy_tags:
        raise Exit("Not a single deploy target selected")
    promote_tags = list(deploy_tags.values()) + [version]
    source_tag = version if is_version_promotion else commit

    # Login with Docker on AWS
    if docker_login:
        aws_docker_login(ctx)

    # Check if version tag already exists in registry
    inspection = ctx.run(f"docker manifest inspect {registry}/{name}:{version}", warn=True)
    version_exists = inspection.exited == 0
    if version_exists:
        print("Skipping version tagging, because version already exists in registry")
        promote_tags.pop()

    # Print some output to know what the command is going to do
    print("Source tag:", source_tag)
    print("Tags added by promotion:", promote_tags)

    # Pull the source images
    ctx.run(f"docker pull {registry}/{name}:{source_tag}", echo=True, pty=True)
    ctx.run(f"docker pull {registry}/{name}-nginx:{source_tag}", echo=True, pty=True)

    # Tagging and pushing of our image and nginx image with relevant tags
    for promote_tag in promote_tags:
        ctx.run(f"docker tag {registry}/{name}:{source_tag} {registry}/{name}:{promote_tag}", echo=True)
        ctx.run(f"docker push {registry}/{name}:{promote_tag}", echo=True, pty=True)
        ctx.run(f"docker tag {registry}/{name}-nginx:{source_tag} {registry}/{name}-nginx:{promote_tag}", echo=True)
        ctx.run(f"docker push {registry}/{name}-nginx:{promote_tag}", echo=True, pty=True)


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
    session = boto3.Session(profile_name=ctx.config.aws.production.profile_name)
    ecr = session.client("ecr")

    # List images
    production_account = ctx.config.aws.production.account
    response = ecr.list_images(
        registryId=production_account,
        repositoryName=name,
    )

    # Print output
    def image_version_sort(image):
        return tuple([int(section) for section in image["imageTag"].split(".")])
    images = [image for image in response["imageIds"] if "imageTag" in image and "." in image["imageTag"]]
    images.sort(key=image_version_sort, reverse=True)
    print(json.dumps(images[:10], indent=4))
