import os
from datetime import date
from fabric import task
from invoke import task as local_task, Responder, Exit


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


@task(name="upload_database")
def upload_database(conn, dump_file):
    if conn.host != conn.config.aws.bastion:
        raise Exit(f"Did not expect the host {conn.host} while the bastion is {conn.config.aws.bastion}")
    if conn.config.env != "production":
        raise Exit("Please migrate legacy database only to production and create snapshot from there")

    dump_directory = os.path.join("postgres", "dumps")
    dump_file_path = os.path.join(dump_directory, dump_file)
    print("Uploading database dump:", dump_file_path)

    # Make minor adjustments to dumps for legacy dumps to work on AWS
    print("Migrating dump file")
    conn.local(f"sed -i.bak 's/OWNER TO surf/OWNER TO postgres/g' {dump_file_path}", echo=True)

    print("Uploading snapshot through port-forwarding")
    # Setup auto-responder
    postgres_user = conn.config.postgres.user
    postgres_password = conn.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern=r"Password: ", response=postgres_password + "\n")
    # Run Postgres command with port forwarding
    with conn.forward_local(local_port=1111, remote_host=conn.config.postgres.host, remote_port=5432):
        conn.local(f"psql -h localhost -p 1111 -U {postgres_user} -W -d edushare -f {dump_file_path}",
                   echo=True, watchers=[postgres_password_responder], pty=True)

    conn.local(f"rm {dump_file_path}.bak", warn=True)
    print("Done")


@local_task(name="upload_media")
def upload_media(ctx):
    media = os.path.join("media", "communities")
    ctx.run(
        f"AWS_PROFILE={ctx.config.aws.profile_name} aws s3 sync {media} "
        f"s3://{ctx.config.aws.image_upload_bucket}/communities",
        echo=True
    )
