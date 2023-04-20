import os

from invoke import task, Exit


@task(name="sync_repository_state", help={
    "push": "Specify this flag to push your local files to production instead of pulling them",
    "no_profile": "Do not use conventional profiles to connect to the S3 bucket, but leave profile unspecified instead",
    "bucket_prefix": "Prefix for the S3 bucket name to use. Defaults to AWS profile for the repository"
})
def sync_repository_state(ctx, push=False, no_profile=False, bucket_prefix=None):
    """
    Performs a pull or push from local filesystem to a production S3 bucket.

    A pull needs to be performed in order to be able to run tests or make builds.
    APPLICATION_MODE needs to be production in order to run this command.
    """
    if push and ctx.config.service.env != "production":
        raise Exit("Can't push to environment other than production")
    elif push:
        sure = input(
            "You are about to overwrite production configuration with your local configuration. Are you sure? "
        )
        if sure.lower() not in ["y", "yes"]:
            raise Exit("Aborted push of local configuration files to production")
    profile = f"AWS_PROFILE={ctx.config.aws.production.profile_name}" if not no_profile else ""

    local_directory = "."
    bucket_prefix = bucket_prefix or ctx.config.aws.production.profile_name
    repository_state_bucket = f"s3://{bucket_prefix}-repository-state"
    source = repository_state_bucket if not push else local_directory
    destination = local_directory if not push else repository_state_bucket
    targets = [
        ("cp", os.path.join("nginx", "ip-whitelist.conf")),
        ("sync", os.path.join("harvester", "sources", "factories", "fixtures"))
    ]
    for operation, path in targets:
        source_path = os.path.join(source, path)
        destination_path = os.path.join(destination, path)
        ctx.run(f"{profile} aws s3 {operation} {source_path} {destination_path}", echo=True)
