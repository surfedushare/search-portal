import os
import boto3
from invoke import task


@task(name="import_snapshot")
def import_snapshot(ctx, snapshot_name, migrate=True):

    print("Preparing")
    snapshot_file_path = os.path.join("postgres", "dumps", snapshot_name)
    if not os.path.exists(snapshot_file_path):
        # Figure out the snapshot S3 key
        # Listing all snapshots and taking the latest if none are specified
        session = boto3.Session()
        s3 = session.client("s3")
        bucket_name = "edushare-data"
        if snapshot_name:
            snapshot_key = "databases/" + snapshot_name
        else:
            listing = s3.list_objects(Bucket=bucket_name, Prefix="databases")
            snapshots = listing["Contents"]
            snapshots.sort(key=lambda snapshot: snapshot["LastModified"], reverse=True)
            snapshot_key = snapshots[0]["Key"]
        # Downloading snapshot file
        print("Downloading:", snapshot_key)
        s3.download_file(Bucket=bucket_name, Key=snapshot_key, Filename=snapshot_file_path)

    if migrate:
        print("Migrating dump file")
        ctx.run(f"sed -i 's/OWNER TO surf/OWNER TO postgres/g' {snapshot_file_path}", echo=True)

    print("Importing snapshot")
    ctx.run(f"psql -h localhost -U postgres -d edushare -f {snapshot_file_path}")
