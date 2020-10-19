from invoke import task, Responder

from commands.postgres.download import download_snapshot


@task(name="import_snapshot", help={
    "snapshot_name": "The file name of the snapshot you want to restore. Defaults to last updated snapshot"
})
def import_snapshot(ctx, snapshot_name=None):

    snapshot_file_path = download_snapshot(snapshot_name)

    # Setup auto-responser.
    # Administrative postgres user on localhost will always be postgres (depends on POSTGRES_USER environment variable)
    postgres_password = ctx.config.secrets.postgres.password
    postgres_password_responder = Responder(pattern="Password", response=postgres_password + "\n")

    print("Importing snapshot")
    ctx.run(f"psql -h localhost -U postgres -d edushare -f {snapshot_file_path}",
            pty=True, watchers=[postgres_password_responder])
    ctx.run(f"rm {snapshot_file_path}.bak", warn=True)
