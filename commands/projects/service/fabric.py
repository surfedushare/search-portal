import os
from datetime import date
from invoke import Responder, Exit
from fabric import task

from commands.postgres.download import download_snapshot


@task()
def create_snapshot(conn):
    """
    Dumps database content as SQL creating a snapshot that other nodes can load easily
    """
    if conn.host != conn.config.aws.bastion:
        raise Exit("Did not expect the host {conn.host} while the bastion is {conn.config.aws.bastion}")

    today = date.today()
    dump_file = f"edushare.{today:%Y-%m-%d}.postgres.sql"
    dump_file_path = os.path.join("postgres", "dumps", dump_file)
    print("Creating snapshot:", dump_file)

    excluded_tables = [
        "django*", "auth*", "social_auth*", "users*",
        "communities_team", "filters_filter", "surfconext_datagoalpermission",
    ]
    excluded_table_flags = " ".join([
        f'-T "{excluded_table}"'
        for excluded_table in excluded_tables
    ])

    # Setup auto-responder
    postgres_user = conn.config.postgres.user
    postgres_password = conn.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern=r"Password: ", response=postgres_password + "\n")
    # Run Postgres command with port forwarding
    with conn.forward_local(local_port=1111, remote_host=conn.config.postgres.host, remote_port=5432):
        conn.local(
            f"pg_dump -h localhost -p 1111 -U {postgres_user} {excluded_table_flags} -c edushare > {dump_file_path}",
            echo=True, watchers=[postgres_password_responder], pty=True
        )

    print("Uploading database to S3")
    conn.local(f"aws s3 cp {dump_file_path} s3://edushare-data/databases/")

    print("Done")


@task(help={
    "snapshot_name": "The file name of the snapshot you want to restore. Defaults to last updated snapshot",
    "migrate": "Whether to apply some changes to the snapshot file to migrate from a pre-AWS format"
})
def restore_snapshot(conn, snapshot_name=None, migrate=True):
    """
    Loads a particular snapshot into the database on AWS through a bastion host
    """
    if conn.host != conn.config.aws.bastion:
        raise Exit(f"Did not expect the host {conn.host} while the bastion is {conn.config.aws.bastion}")
    if conn.config.env == "production":
        raise Exit("Cowardly refusing to restore the production database")

    snapshot_file_path = download_snapshot(snapshot_name)

    # Make minor adjustments to dumps for legacy dumps to work on AWS
    if migrate:
        print("Migrating dump file")
        conn.local(f"sed -i.bak 's/OWNER TO surf/OWNER TO postgres/g' {snapshot_file_path}", echo=True)

    if "test" in conn.config.surfconext.oidc_endpoint:
        print("Rewriting team ARN's for test communities")
        production_test_team_urn = "urn:collab:group:surfteams.nl:nl:surfnet:diensten:test_team_zoekportal"
        development_test_team_urn = "urn:collab:group:test.surfconext.nl:nl:surfnet:diensten:zoekportaal_test_community"
        conn.local(f"sed -i.bak 's/{production_test_team_urn}/{development_test_team_urn}/g' {snapshot_file_path}",
                   echo=True)

    print("Restoring snapshot")
    # Setup auto-responder
    postgres_user = conn.config.postgres.user
    postgres_password = conn.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern=r"Password: ", response=postgres_password + "\n")
    # Run Postgres command with port forwarding
    with conn.forward_local(local_port=1111, remote_host=conn.config.postgres.host, remote_port=5432):
        conn.local(f"psql -h localhost -p 1111 -U {postgres_user} -W -d edushare -f {snapshot_file_path}",
                   echo=True, watchers=[postgres_password_responder], pty=True)

    conn.local(f"rm {snapshot_file_path}.bak", warn=True)
    print("Done")
