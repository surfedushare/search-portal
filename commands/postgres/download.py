import os
import boto3

from commands import ROOT_DIR


def download_snapshot(snapshot_name, bucket_name, profile_name):

    print("Preparing download")
    session = boto3.Session(profile_name=profile_name)
    s3 = session.client("s3")
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
    snapshot_file_path = os.path.join(ROOT_DIR, "postgres", "dumps", snapshot_name)
    if not os.path.exists(snapshot_file_path):
        print("Downloading:", snapshot_key)
        s3.download_file(Bucket=bucket_name, Key=snapshot_key, Filename=snapshot_file_path)
    else:
        print(f"Snapshot exists: {snapshot_file_path}")

    return snapshot_file_path
