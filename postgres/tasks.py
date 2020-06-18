import os
import boto3
from invoke import task, Responder


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def download_snapshot(snapshot_name):

    print("Preparing download")
    session = boto3.Session(profile_name="pol-dev")
    s3 = session.client("s3")
    bucket_name = "edushare-data"
    # Figure out the snapshot S3 key
    # Listing all snapshots and taking the latest if none are specified
    if snapshot_name:
        snapshot_key = "databases/" + snapshot_name
    else:
        listing = s3.list_objects(Bucket=bucket_name, Prefix="databases")
        snapshots = listing["Contents"]
        snapshots.sort(key=lambda snapshot: snapshot["LastModified"], reverse=True)
        snapshot_key = snapshots[0]["Key"]
        bucket_path, snapshot_name = os.path.split(snapshot_key)

    # Downloading snapshot file if it doesn't exist
    snapshot_file_path = os.path.join(BASE_DIR, "postgres", "dumps", snapshot_name)
    if not os.path.exists(snapshot_file_path):
        print("Downloading:", snapshot_key)
        s3.download_file(Bucket=bucket_name, Key=snapshot_key, Filename=snapshot_file_path)
    else:
        print(f"Snapshot exists: {snapshot_file_path}")

    return snapshot_file_path


@task(name="import_snapshot")
def import_snapshot(ctx, snapshot_name=None, migrate=True):

    snapshot_file_path = download_snapshot(snapshot_name)

    # Setup auto-responser.
    # Administrative postgres user on localhost will always be postgres (depends on POSTGRES_USER environment variable)
    postgres_password = ctx.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern="Password", response=postgres_password + "\n")

    # Make minor adjustments to dumps for legacy dumps to work on AWS
    if migrate:
        print("Migrating dump file")
        ctx.run(f"sed -i.bak 's/OWNER TO surf/OWNER TO postgres/g' {snapshot_file_path}", echo=True)

    print("Importing snapshot")
    ctx.run(f"psql -h localhost -U postgres -d edushare -f {snapshot_file_path}",
            pty=True, watchers=[postgres_password_responder])
