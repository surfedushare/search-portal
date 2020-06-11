import os
import boto3
from invoke import Responder
from fabric import task


@task(name="setup")
def setup(ctx):
    # Setup auto-responder
    postgres_owner_password = ctx.config.secrets.postgres_owner.password
    postgres_passord_responder = Responder(pattern="Password", response= postgres_owner_password + "\n")
    # Run Postgres commands with port forwarding
    with ctx.forward_local(local_port=1111, remote_host=ctx.config.django.postgres_host, remote_port=5432):
        # Clear all databases and application role
        ctx.local(f'psql -h localhost -p 1111 -U postgres -W -c "DROP DATABASE edushare"',
                  echo=True, warn=True, watchers=[postgres_passord_responder], pty=True)
        ctx.local(f'psql -h localhost -p 1111 -U postgres -W -c "DROP DATABASE harvester"',
                  echo=True, warn=True, watchers=[postgres_passord_responder], pty=True)
        # Create default database
        ctx.local(f'psql -h localhost -p 1111 -U postgres -W -c "CREATE DATABASE edushare"',
                  echo=True, watchers=[postgres_passord_responder], pty=True)
        # Create application role if it doesn't exist yet
        ctx.local(
            f'psql -h localhost -p 1111 -U postgres -W '
            f'-c "CREATE USER django WITH ENCRYPTED PASSWORD \'{ctx.config.secrets.postgres.password}\'"',
            echo=True, warn=True, watchers=[postgres_passord_responder], pty=True
        )
        # Initialise permissions and other databases
        ctx.local(
            f"psql -h localhost -p 1111 -U postgres -W -f postgres/docker-entrypoint-initdb.d/initdb.sql",
            echo=True, watchers=[postgres_passord_responder], pty=True
        )


@task()
def restore_snapshot(ctx, snapshot_name=None, recreate=True, migrate=True):

    print("Preparing")
    snapshot_file_path = os.path.join("postgres", "dumps", snapshot_name)
    if not os.path.exists(snapshot_file_path):
        # Figure out the snapshot S3 key
        # Listing all snapshots and taking the latest if none are specified
        session = boto3.Session()
        s3 = session.client("s3")
        bucket_name = "edushare-data"
        if snapshot_name:
            snapshot_key = "databases/" + snapshot_name
        else:
            listing = s3.list_objects(Bucket=bucket_name, Prefix="databases")
            snapshots = listing["Contents"]
            snapshots.sort(key=lambda snapshot: snapshot["LastModified"], reverse=True)
            snapshot_key = snapshots[0]["Key"]

        # Downloading snapshot file
        print("Downloading:", snapshot_key)
        s3.download_file(Bucket=bucket_name, Key=snapshot_key, Filename=snapshot_file_path)

    # Make minor adjustments to dumps for legacy dumps to work on AWS
    if migrate:
        print("Migrating dump file")
        ctx.local(f"sed -i 's/OWNER TO surf/OWNER TO postgres/g' {snapshot_file_path}", echo=True)

    # Recreating database with all correct privileges
    if recreate:
        print("Recreating databases")
        setup(ctx)

    print("Restoring snapshot")
    # Setup auto-responder
    postgres_owner_password = ctx.config.secrets.postgres_owner.password
    postgres_passord_responder = Responder(pattern=r"Password: ", response=postgres_owner_password + "\n")
    # Run Postgres command with port forwarding
    with ctx.forward_local(local_port=1111, remote_host=ctx.config.django.postgres_host, remote_port=5432):
        ctx.local(f"psql -h localhost -p 1111 -U postgres -W -d edushare -f {snapshot_file_path}",
                  echo=True, watchers=[postgres_passord_responder], pty=True)

    print("Done")
