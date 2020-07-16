from invoke import Responder
from fabric import task
from getpass import getpass
import signal

from django.conf import settings
from django.contrib.auth.hashers import make_password


@task(name="create_super_user")
def create_super_user(ctx):
    """
    Inserts a superuser with raw SQL into Django user table to be used for login to harvester
    """

    # Setup auto-responder
    postgres_user = ctx.config.django.postgres_user
    postgres_password = ctx.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern="Password", response=postgres_password + "\n")

    # Gather input from user
    settings.configure()
    username = input("Username:")
    password = make_password(getpass())

    # Run Postgres command with port forwarding
    with ctx.forward_local(local_port=1111, remote_host=ctx.config.django.postgres_host, remote_port=5432):
        # Adds raw password to not send passwords through AWS ECS task configurations
        escaped_password = password.replace("$", r"\$")
        ctx.local(f'psql -h localhost -p 1111 -U {postgres_user} -d harvester -W -c "'
                  f'INSERT INTO auth_user '
                  f'(password, is_superuser, is_staff, is_active, username, first_name, last_name, email, date_joined) '
                  f'VALUES (\'{escaped_password}\', true, true, true, \'{username}\', \'\', \'\', \'\', NOW())"',
                  echo=True, warn=True, watchers=[postgres_password_responder], pty=True)


@task(name="connect_uwsgi")
def connect_uwsgi(ctx):
    """
    Forwards a port to the harvester service UWSGI server. Useful to inspect harvests through the admin.
    """
    print("Admin interface available with SSH encryption at: http://localhost:2222/admin/")
    with ctx.forward_local(local_port=2222, remote_host="harvester.pol", remote_port=8080):
        signal.pause()
