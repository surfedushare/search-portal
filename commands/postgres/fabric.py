import os
from datetime import date
from invoke import Responder, Exit
from fabric import task

from commands.postgres.download import download_snapshot
from commands.postgres.sql import insert_django_user_statement, setup_database_statements


@task(name="setup_postgres")
def setup_postgres_remote(conn):
    """
    Sets up databases and roles with correct permissions inside AWS through a bastion host
    """
    if conn.host != conn.config.aws.bastion:
        raise Exit(f"Did not expect the host {conn.host} while the bastion is {conn.config.aws.bastion}")
    if conn.config.env == "production":
        raise Exit("Cowardly refusing to recreate the production database")

    # Setup auto-responder
    postgres_user = conn.config.django.postgres_user
    postgres_password = conn.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern="Password", response=postgres_password + "\n")
    # Run Postgres commands with port forwarding
    with conn.forward_local(local_port=1111, remote_host=conn.config.django.postgres_host, remote_port=5432):
        # Run Postgres commands to recreate the database and roles
        global_statements, database_statements = setup_database_statements(
            database_name=conn.config.postgres.database,
            root_user=postgres_user,
            application_user=conn.config.postgres.application_user,
            application_password=conn.config.secrets.postgres.application_password
        )
        for statement in global_statements:
            # Run SQL statements that are not specific for a database
            conn.local(
                f'psql -h localhost -U {postgres_user} -W -c "{statement}"',
                echo=True,
                pty=True,
                warn=True,
                watchers=[postgres_password_responder]
            )
        for statement in database_statements:
            # Run SQL statements per database
            conn.local(
                f'psql -h localhost -U {postgres_user} -W -d {conn.config.postgres.database} -c "{statement}"',
                echo=True,
                pty=True,
                warn=True,
                watchers=[postgres_password_responder]
            )
        # Migrate the application
        conn.local(
            f"cd {conn.config.django.directory} && "
            f"AWS_PROFILE={conn.config.aws.profile_name} "
            f"POL_DJANGO_POSTGRES_HOST=localhost "
            f"POL_DJANGO_POSTGRES_PORT=1111 "
            f"python manage.py migrate",
            echo=True, pty=True
        )
        # Create generic superuser named supersurf
        admin_password = conn.config.secrets.django.admin_password
        insert_user = insert_django_user_statement(
            "supersurf", admin_password, is_edushare=conn.config.postgres.database == "edushare"
        )
        conn.local(
            f'psql -h localhost -p 1111 -U {postgres_user} -d edushare -W -c "{insert_user}"',
            echo=True,
            pty=True,
            warn=True,
            watchers=[postgres_password_responder],
        )
