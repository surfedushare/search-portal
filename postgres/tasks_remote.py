from invoke import Responder
from fabric import task

from .tasks_local import download_snapshot


@task(name="setup")
def setup(ctx):
    """
    Sets up databases and roles with correct permissions inside AWS through a bastion host
    """

    # Setup auto-responder
    postgres_user = ctx.config.django.postgres_user
    postgres_password = ctx.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern="Password", response=postgres_password + "\n")
    # Run Postgres commands with port forwarding
    with ctx.forward_local(local_port=1111, remote_host=ctx.config.django.postgres_host, remote_port=5432):
        # Clear all databases and application role
        ctx.local(f'psql -h localhost -p 1111 -U {postgres_user} -W -c "DROP DATABASE edushare"',
                  echo=True, warn=True, watchers=[postgres_password_responder], pty=True)
        ctx.local(f'psql -h localhost -p 1111 -U {postgres_user} -W -c "DROP DATABASE harvester"',
                  echo=True, warn=True, watchers=[postgres_password_responder], pty=True)
        ctx.local(f'psql -h localhost -p 1111 -U {postgres_user} -W -c "DROP OWNED BY postgres"',
                  echo=True, warn=True, watchers=[postgres_password_responder], pty=True)
        ctx.local(f'psql -h localhost -p 1111 -U {postgres_user} -W -c "DROP USER django"',
                  echo=True, warn=True, watchers=[postgres_password_responder], pty=True)
        # Create default database
        ctx.local(f'psql -h localhost -p 1111 -U {postgres_user} -W -c "CREATE DATABASE edushare"',
                  echo=True, watchers=[postgres_password_responder], pty=True)
        # Create application role if it doesn't exist yet
        ctx.local(
            f'psql -h localhost -p 1111 -U {postgres_user} -W '
            f'-c "CREATE USER django WITH ENCRYPTED PASSWORD \'{ctx.config.secrets.postgres_application.password}\'"',
            echo=True, warn=True, watchers=[postgres_password_responder], pty=True
        )
        # Initialise permissions and other databases
        ctx.local(
            f"psql -h localhost -p 1111 -U {postgres_user} -W -f postgres/docker-entrypoint-initdb.d/initdb.sql",
            echo=True, watchers=[postgres_password_responder], pty=True
        )
        ctx.local(
            f"psql -h localhost -p 1111 -U {postgres_user} -d edushare -W -f "
            f"postgres/docker-entrypoint-initdb.d/set-default-privileges.tpl",
            echo=True, watchers=[postgres_password_responder], pty=True
        )
        ctx.local(
            f"psql -h localhost -p 1111 -U {postgres_user} -d harvester -W -f "
            f"postgres/docker-entrypoint-initdb.d/set-default-privileges.tpl",
            echo=True, watchers=[postgres_password_responder], pty=True
        )


@task(help={
    "snapshot_name": "The file name of the snapshot you want to restore. Defaults to last updated snapshot",
    "recreate": "Whether to completely destroy the database prior to loading the data",
    "migrate": "Whether to apply some changes to the snapshot file to migrate from a pre-AWS format"
})
def restore_snapshot(ctx, snapshot_name=None, recreate=True, migrate=True):
    """
    Loads a particular snapshot into the database on AWS through a bastion host
    """

    snapshot_file_path = download_snapshot(snapshot_name)

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
    postgres_user = ctx.config.django.postgres_user
    postgres_password = ctx.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern=r"Password: ", response=postgres_password + "\n")
    # Run Postgres command with port forwarding
    with ctx.forward_local(local_port=1111, remote_host=ctx.config.django.postgres_host, remote_port=5432):
        ctx.local(f"psql -h localhost -p 1111 -U {postgres_user} -W -d edushare -f {snapshot_file_path}",
                  echo=True, watchers=[postgres_password_responder], pty=True)

    print("Done")
