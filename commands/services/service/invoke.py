import os
from invoke import task, Responder, Exit

from environments.project.configuration import create_configuration
from commands.postgres.download import download_snapshot
from commands.postgres.sql import insert_django_user_statement


@task(name="import_snapshot", help={
    "snapshot_name": "The file name of the snapshot you want to restore. Defaults to last updated snapshot"
})
def import_snapshot(ctx, source_profile, snapshot_name=None):

    snapshot_file_path = download_snapshot(snapshot_name, ctx.config.aws.search_content_bucket, source_profile)
    database = ctx.config.postgres.database

    # Setup auto-responser.
    # Administrative postgres user on localhost will always be postgres (depends on POSTGRES_USER environment variable)
    postgres_password = ctx.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern="Password", response=postgres_password + "\n")

    print("Importing snapshot")
    ctx.run(f"psql -h localhost -U postgres -d {database} -f {snapshot_file_path}",
            pty=True, watchers=[postgres_password_responder])

    print("creating superuser")
    admin_password = ctx.config.secrets.django.admin_password
    harvester_key = ctx.config.secrets.harvester.api_key
    insert_user = insert_django_user_statement(
        "supersurf", admin_password, harvester_key, is_search_service=True
    )
    ctx.run(
        f'psql -h localhost -U postgres -d {database} -W -c "{insert_user}"',
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
    if ctx.config.service.env == "production":
        raise Exit("Cowardly refusing to use production as a destination environment")

    local_directory = "media"
    source_config = create_configuration(source, service="service", context="host")
    source = source_config.aws.image_upload_bucket
    source = "s3://" + source if source is not None else local_directory
    destination = ctx.config.aws.image_upload_bucket
    destination = "s3://" + destination if destination is not None else local_directory

    source_path = os.path.join(source, path)
    destination_path = os.path.join(destination, path)
    profile_name = ctx.config.aws.profile_name or "pol-prod"
    ctx.run(f"AWS_PROFILE={profile_name} aws s3 sync {source_path} {destination_path}", echo=True)


@task(name="make_translations")
def make_translations(ctx):
    """
    Scans the code for translatable messages and aggregates them in a .po file
    """
    with ctx.cd("service"):
        ctx.run(
            "python manage.py makemessages -l en "
            "--settings=surf.settings.base "
            "--ignore 'surf/vendor/*'"
        )
