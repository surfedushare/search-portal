import os
from datetime import date
from invoke import Responder, Exit
from fabric import task

from commands.postgres.download import download_snapshot
from commands.postgres.sql import insert_django_user_statement


@task()
def create_snapshot(conn):
    """
    Dumps database content as SQL creating a snapshot that other nodes can load easily
    """
    if conn.host != conn.config.aws.bastion:
        raise Exit(f"Did not expect the host {conn.host} while the bastion is {conn.config.aws.bastion}")

    database = conn.config.postgres.database
    today = date.today()
    dump_file = f"{database}.{today:%Y-%m-%d}.postgres.sql"
    dump_file_path = os.path.join("postgres", "dumps", dump_file)
    print("Creating snapshot:", dump_file)

    excluded_tables = [
        "django_session", "auth*", "social_auth*", "users*",
        "communities_team", "filters_filter", "surfconext_datagoalpermission",
    ]
    excluded_table_flags = " ".join([
        f'--exclude-table-data="{excluded_table}"'
        for excluded_table in excluded_tables
    ])

    # Setup auto-responder
    postgres_user = conn.config.postgres.user
    postgres_password = conn.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern=r"Password: ", response=postgres_password + "\n")
    # Run Postgres command with port forwarding
    with conn.forward_local(local_port=1111, remote_host=conn.config.postgres.host, remote_port=5432):
        conn.local(
            f"pg_dump -h localhost -p 1111 -U {postgres_user} {excluded_table_flags} -c {database} > {dump_file_path}",
            echo=True, watchers=[postgres_password_responder], pty=True
        )

    print("Uploading database to S3")
    conn.local(f"aws s3 cp {dump_file_path} s3://{conn.config.aws.search_content_bucket}/databases/")

    print("Done")


@task(help={
    "snapshot_name": "The file name of the snapshot you want to restore. Defaults to last updated snapshot"
})
def restore_snapshot(conn, source_profile, snapshot_name=None):
    """
    Loads a particular snapshot into the database on AWS through a bastion host
    """
    if conn.host != conn.config.aws.bastion:
        raise Exit(f"Did not expect the host {conn.host} while the bastion is {conn.config.aws.bastion}")
    if conn.config.service.env == "production":
        raise Exit("Cowardly refusing to restore the production database")

    snapshot_file_path = download_snapshot(snapshot_name, conn.config.aws.search_content_bucket, source_profile)
    database = conn.config.postgres.database

    print("Restoring snapshot")
    # Setup auto-responder
    postgres_user = conn.config.postgres.user
    postgres_password = conn.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern=r"Password: ", response=postgres_password + "\n")

    # Run Postgres command with port forwarding
    with conn.forward_local(local_port=1111, remote_host=conn.config.postgres.host, remote_port=5432):
        # Restore actual database
        conn.local(f"psql -h localhost -p 1111 -U {postgres_user} -W -d {database} -f {snapshot_file_path}",
                   echo=True, watchers=[postgres_password_responder], pty=True)
        # Create generic superuser named supersurf
        admin_password = conn.config.secrets.django.admin_password
        harvester_key = conn.config.secrets.harvester.api_key
        insert_user = insert_django_user_statement(
            "supersurf", admin_password, harvester_key, is_search_service=conn.config.service.name == "service"
        )
        conn.local(
            f'psql -h localhost -p 1111 -U {postgres_user} -d {conn.config.postgres.database} -W -c "{insert_user}"',
            echo=True,
            pty=True,
            warn=True,
            watchers=[postgres_password_responder],
        )

    conn.local(f"rm {snapshot_file_path}.bak", warn=True)
    print("Done")
