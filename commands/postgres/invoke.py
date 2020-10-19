from invoke import Responder
from fabric import task

from commands.postgres.sql import setup_database_statements
from commands.postgres.sql import insert_django_user_statement


@task(name="setup_postgres")
def setup_postgres_localhost(ctx):
    """
    Sets up the postgres databases and roles with correct permissions on localhost
    """
    # Setup auto-responder
    postgres_user = ctx.config.postgres.user  # should be root user at runtime
    postgres_password = ctx.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern="Password", response=postgres_password + "\n")
    # Run Postgres commands to recreate the database and roles
    global_statements, database_statements = setup_database_statements(
        database_name=ctx.config.postgres.database,
        root_user=postgres_user,
        application_user=ctx.config.postgres.application_user,
        application_password=ctx.config.secrets.postgres.application_password,
        allow_tests=True
    )
    for statement in global_statements:
        # Run SQL statements that are not specific for a database
        ctx.run(
            f'psql -h localhost -U {postgres_user} -W -c "{statement}"',
            echo=True,
            pty=True,
            warn=True,
            watchers=[postgres_password_responder]
        )
    for statement in database_statements:
        # Run SQL statements per database
        ctx.run(
            f'psql -h localhost -U {postgres_user} -W -d {ctx.config.postgres.database} -c "{statement}"',
            echo=True,
            pty=True,
            warn=True,
            watchers=[postgres_password_responder]
        )
    # Migrate the application
    ctx.run(
        f"cd {ctx.config.django.directory} && python manage.py migrate",
        echo=True, pty=True
    )
    # Create generic superuser named supersurf
    admin_password = ctx.config.secrets.django.admin_password
    insert_user = insert_django_user_statement(
        "supersurf", admin_password, is_edushare=ctx.config.postgres.database == "edushare"
    )
    ctx.run(
        f'psql -h localhost -U {postgres_user} -d {ctx.config.postgres.database} -W -c "{insert_user}"',
        echo=True,
        pty=True,
        warn=True,
        watchers=[postgres_password_responder],
    )
    # Load data fixtures to get the project going
    for fixture in ctx.config.django.fixtures:
        ctx.run(
            f"cd {ctx.config.django.directory} && python manage.py loaddata {fixture}",
            echo=True, pty=True
        )
