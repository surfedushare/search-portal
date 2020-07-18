from invoke import Responder
from fabric import task

from .tasks_local import download_snapshot


@task(name="setup")
def setup(conn):
    """
    Sets up databases and roles with correct permissions inside AWS through a bastion host
    """
    if conn.host != conn.config.aws.bastion:
        raise Exit(f"Did not expect the host {conn.host} while the bastion is {conn.config.aws.bastion}")

    # Setup auto-responder
    postgres_user = conn.config.django.postgres_user
    postgres_password = conn.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern="Password", response=postgres_password + "\n")
    # Run Postgres commands with port forwarding
    with conn.forward_local(local_port=1111, remote_host=conn.config.django.postgres_host, remote_port=5432):
        # Clear all databases and application role
        conn.local(f'psql -h localhost -p 1111 -U {postgres_user} -W -c "DROP DATABASE edushare"',
                  echo=True, warn=True, watchers=[postgres_password_responder], pty=True)
        conn.local(f'psql -h localhost -p 1111 -U {postgres_user} -W -c "DROP DATABASE harvester"',
                  echo=True, warn=True, watchers=[postgres_password_responder], pty=True)
        conn.local(f'psql -h localhost -p 1111 -U {postgres_user} -W -c "DROP OWNED BY postgres"',
                  echo=True, warn=True, watchers=[postgres_password_responder], pty=True)
        conn.local(f'psql -h localhost -p 1111 -U {postgres_user} -W -c "DROP USER django"',
                  echo=True, warn=True, watchers=[postgres_password_responder], pty=True)
        # Create default database
        conn.local(f'psql -h localhost -p 1111 -U {postgres_user} -W -c "CREATE DATABASE edushare"',
                  echo=True, watchers=[postgres_password_responder], pty=True)
        # Create application role if it doesn't exist yet
        conn.local(
            f'psql -h localhost -p 1111 -U {postgres_user} -W '
            f'-c "CREATE USER django WITH ENCRYPTED PASSWORD \'{ctx.config.secrets.postgres_application.password}\'"',
            echo=True, warn=True, watchers=[postgres_password_responder], pty=True
        )
        # Initialise permissions and other databases
        conn.local(
            f"psql -h localhost -p 1111 -U {postgres_user} -W -f postgres/docker-entrypoint-initdb.d/initdb.sql",
            echo=True, watchers=[postgres_password_responder], pty=True
        )
        conn.local(
            f"psql -h localhost -p 1111 -U {postgres_user} -d edushare -W -f "
            f"postgres/docker-entrypoint-initdb.d/set-default-privileges.tpl",
            echo=True, watchers=[postgres_password_responder], pty=True
        )
        conn.local(
            f"psql -h localhost -p 1111 -U {postgres_user} -d harvester -W -f "
            f"postgres/docker-entrypoint-initdb.d/set-default-privileges.tpl",
            echo=True, watchers=[postgres_password_responder], pty=True
        )


@task(help={
    "snapshot_name": "The file name of the snapshot you want to restore. Defaults to last updated snapshot",
    "recreate": "Whether to completely destroy the database prior to loading the data",
    "migrate": "Whether to apply some changes to the snapshot file to migrate from a pre-AWS format"
})
def restore_snapshot(conn, snapshot_name=None, recreate=True, migrate=True):
    """
    Loads a particular snapshot into the database on AWS through a bastion host
    """
    if conn.host != conn.config.aws.bastion:
        raise Exit(f"Did not expect the host {conn.host} while the bastion is {conn.config.aws.bastion}")

    snapshot_file_path = download_snapshot(snapshot_name)

    # Make minor adjustments to dumps for legacy dumps to work on AWS
    if migrate:
        print("Migrating dump file")
        conn.local(f"sed -i 's/OWNER TO surf/OWNER TO postgres/g' {snapshot_file_path}", echo=True)

    # Recreating database with all correct privileges
    if recreate:
        print("Recreating databases")
        setup(conn)

    print("Restoring snapshot")
    # Setup auto-responder
    postgres_user = conn.config.django.postgres_user
    postgres_password = conn.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern=r"Password: ", response=postgres_password + "\n")
    # Run Postgres command with port forwarding
    with conn.forward_local(local_port=1111, remote_host=ctx.config.django.postgres_host, remote_port=5432):
        conn.local(f"psql -h localhost -p 1111 -U {postgres_user} -W -d edushare -f {snapshot_file_path}",
                  echo=True, watchers=[postgres_password_responder], pty=True)

    print("Done")
