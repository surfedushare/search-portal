from invoke import Exit
from fabric import task
import signal


@task(name="connect_uwsgi")
def connect_uwsgi(conn):
    """
    Forwards a port to the harvester service UWSGI server. Useful to inspect harvests through the admin.
    """
    if conn.host != conn.config.aws.bastion:
        raise Exit(f"Did not expect the host {conn.host} while the bastion is {conn.config.aws.bastion}")

    print("Admin interface available with SSH encryption at: http://localhost:2222/admin/")
    with conn.forward_local(local_port=2222, remote_host="harvester.pol", remote_port=8080):
        signal.pause()


@task(name="connect_flower")
def connect_flower(conn):
    """
    Forwards a port to the harvester flow-er server. Useful to inspect Celery health.
    """
    if conn.host != conn.config.aws.bastion:
        raise Exit(f"Did not expect the host {conn.host} while the bastion is {conn.config.aws.bastion}")

    print("Flow-er dashboard available with SSH encryption at: http://localhost:3333/")
    with conn.forward_local(local_port=3333, remote_host="harvester.pol", remote_port=5555):
        signal.pause()


@task(name="connect_with_shell")
def connect_with_shell(conn):
    """
    Forwards Postgres and Elastic Search ports and starts a Django shell to debug remote data.
    """
    if conn.host != conn.config.aws.bastion:
        raise Exit(f"Did not expect the host {conn.host} while the bastion is {conn.config.aws.bastion}")

    print(f"Starting Python shell with Django models loaded connected to {conn.config.env}")
    with conn.forward_local(local_port=9223, remote_host=conn.config.elastic_search.host, remote_port=443):
        with conn.forward_local(local_port=5433, remote_host=conn.config.postgres.host, remote_port=5432):
            conn.local(
                f"cd {conn.config.django.directory} && "
                f"AWS_PROFILE={conn.config.aws.profile_name} "
                f"POL_ELASTIC_SEARCH_HOST=localhost:9223 "
                f"POL_ELASTIC_SEARCH_VERIFY_CERTS=0 "
                f"POL_POSTGRES_HOST=localhost "
                f"POL_POSTGRES_PORT=5433 "
                f"python manage.py shell",
                echo=True, pty=True
            )
