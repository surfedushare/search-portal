import os
from datetime import date
from fabric import task
from invoke import task as local_task


@task(name="download_database")
def download_database(connection):
    # Create dump
    rsl = connection.sudo("docker ps -qf label=nl.surfcatalog.db", echo=True, pty=True)
    container_id = rsl.stdout.split("\n")[1].strip()
    connection.sudo(
        f"docker exec -i {container_id} pg_dump -h localhost -U surf -c surf > edushare.postgres.sql",
        echo=True,
        pty=True
    )
    # Prepare downloads locally
    dump_directory = os.path.join("postgres", "dumps")
    os.makedirs(dump_directory, exist_ok=True)
    # Download dump to local
    today = date.today()
    dump_file = f"edushare.{today:%Y-%m-%d}.postgres.sql"
    connection.get("edushare.postgres.sql", f"{dump_directory}/{dump_file}")
    print("Downloaded:", dump_file)


@local_task(name="download_media")
def download_media(ctx):
    ctx.run("rsync -zrthv --progress --delete legacy.zoekportaal:/volumes/surf/media/communities media/")


@local_task(name="upload_database")
def upload_database(ctx, dump_file):
    target_file = os.path.join("postgres", "dumps", dump_file)
    ctx.run(f"aws s3 cp {target_file} s3://edushare-data/databases/", echo=True)


@local_task(name="upload_media")
def upload_media(ctx):
    media = os.path.join("media", "communities")
    ctx.run(
        f"AWS_PROFILE={ctx.config.aws.profile_name} aws s3 sync {media} "
        f"s3://{ctx.config.aws.image_upload_bucket}/communities",
        echo=True
    )
