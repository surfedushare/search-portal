from invoke import task, Responder

from commands.postgres.download import download_snapshot


@task(name="import_snapshot", help={
    "snapshot_name": "The file name of the snapshot you want to restore. Defaults to last updated snapshot",
    "migrate": "Whether to apply some changes to the snapshot file to migrate from a pre-AWS format"
})
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
    ctx.run(f"rm {snapshot_file_path}.bak", warn=True)
