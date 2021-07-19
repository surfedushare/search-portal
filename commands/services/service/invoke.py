import os
from invoke import task, Responder, Exit

from environments.surfpol.configuration import create_configuration
from commands.postgres.download import download_snapshot
from commands.postgres.sql import insert_django_user_statement
from commands.aws.ecs import run_task


@task(name="import_snapshot", help={
    "snapshot_name": "The file name of the snapshot you want to restore. Defaults to last updated snapshot"
})
def import_snapshot(ctx, snapshot_name=None):

    snapshot_file_path = download_snapshot(snapshot_name)

    # Setup auto-responser.
    # Administrative postgres user on localhost will always be postgres (depends on POSTGRES_USER environment variable)
    postgres_password = ctx.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern="Password", response=postgres_password + "\n")

    print("Importing snapshot")
    ctx.run(f"psql -h localhost -U postgres -d edushare -f {snapshot_file_path}",
            pty=True, watchers=[postgres_password_responder])

    print("creating superuser")
    admin_password = ctx.config.secrets.django.admin_password
    insert_user = insert_django_user_statement(
        "supersurf", admin_password, is_edushare=True
    )
    ctx.run(
        f'psql -h localhost -U postgres -d edushare -W -c "{insert_user}"',
        echo=True,
        pty=True,
        warn=True,
        watchers=[postgres_password_responder],
    )

    print("Cleanup")
    ctx.run(f"rm {snapshot_file_path}.bak", warn=True)


@task(name="sync_upload_media", help={
    "source": "The source you want to sync media uploads from",
    "path": "The uploads path you want to sync"
})
def sync_upload_media(ctx, source="production", path="communities"):
    """
    Performs a sync between the upload media buckets of two environments.
    APPLICATION_MODE determines the destination environment.
    """
    if ctx.config.env == "production":
        raise Exit("Cowardly refusing to use production as a destination environment")

    local_directory = "media"
    source_config = create_configuration(source, project="service", context="host")
    source = source_config.aws.image_upload_bucket
    source = "s3://" + source if source is not None else local_directory
    destination = ctx.config.aws.image_upload_bucket
    destination = "s3://" + destination if destination is not None else local_directory

    source_path = os.path.join(source, path)
    destination_path = os.path.join(destination, path)
    ctx.run(f"AWS_PROFILE={ctx.config.aws.profile_name} aws s3 sync {source_path} {destination_path}", echo=True)


@task(name="sync_category_filters", help={
    "mode": "Mode you want to sync: localhost, development, acceptance or production. Must match APPLICATION_MODE",
})
def sync_category_filters(ctx, mode):
    """
    Syncs the list of category filters with Elastic Search
    """
    run_task(ctx, "service", mode, ["python", "manage.py", "sync_category_filters"])
