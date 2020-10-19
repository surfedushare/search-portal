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
