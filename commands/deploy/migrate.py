from invoke.tasks import task

from commands.aws.ecs import run_task


@task(help={
    "target": "Name of the project you want migrate on AWS: service or harvester",
    "mode": "Mode you want to migrate: development, acceptance or production. Must match APPLICATION_MODE"
})
def migrate(ctx, target, mode):
    """
    Executes migration task on container cluster for development, acceptance or production environment on AWS
    """
    command = ["python", "manage.py", "migrate"]
    environment = [
        {
            "name": "POL_POSTGRES_USER",
            "value": f"{ctx.config.postgres.user}"
        },
        {
            "name": "POL_SECRETS_POSTGRES_PASSWORD",
            "value": f"{ctx.config.aws.postgres_password_arn}"
        },
    ]
    run_task(ctx, target, mode, command, environment)
