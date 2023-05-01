from invoke import Exit
from fabric import task


@task(name="connect_with_shell")
def connect_with_shell(conn):
    """
    Forwards Postgres ports and starts a Django shell to debug remote data.
    """
    if conn.host != conn.config.aws.bastion:
        raise Exit(f"Did not expect the host {conn.host} while the bastion is {conn.config.aws.bastion}")
    print(
        f"Starting Python shell with Django models loaded connected to {conn.config.service.env} and remote Open Search"
    )
    with conn.forward_local(local_port=5433, remote_host=conn.config.postgres.host, remote_port=5432):
        conn.local(
            f"cd {conn.config.service.directory} && "
            f"AWS_PROFILE={conn.config.aws.profile_name} "
            f"POL_POSTGRES_HOST=localhost "
            f"POL_POSTGRES_PORT=5433 "
            f"python manage.py shell",
            echo=True, pty=True
        )
