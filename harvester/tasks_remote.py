from invoke import Responder, Exit
from fabric import task
from getpass import getpass
import signal

from django.conf import settings

from commands.sql import insert_django_user_statement


@task(name="create_super_user")
def create_super_user(conn):
    """
    Inserts a superuser with raw SQL into Django user table to be used for login to harvester
    """
    if conn.host != conn.config.aws.bastion:
        raise Exit(f"Did not expect the host {conn.host} while the bastion is {conn.config.aws.bastion}")

    # Setup auto-responder
    postgres_user = conn.config.django.postgres_user
    postgres_password = conn.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern="Password", response=postgres_password + "\n")

    # Gather input from user
    settings.configure()
    username = input("Username:")
    password = getpass()

    # Run Postgres command with port forwarding
    with conn.forward_local(local_port=1111, remote_host=conn.config.django.postgres_host, remote_port=5432):
        # Adds raw password to not send passwords through AWS ECS task configurations
        insert_user = insert_django_user_statement(username, password)
        conn.local(
            f'psql -h localhost -p 1111 -U {postgres_user} -d harvester -W -c "{insert_user}"',
            echo=True, warn=True, watchers=[postgres_password_responder], pty=True
        )


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
