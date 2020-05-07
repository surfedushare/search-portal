import os
from elasticsearch import Elasticsearch
try:
    from invoke import ctask as task
except ImportError:
    from invoke import task


def get_es_client(ctx, silent=False):
    """
    Returns the elasticsearch client which uses the configuration file
    """
    protocol = ctx.elastic_search.protocol
    protocol_config = {} if protocol == "http" else {"scheme": "https", "port": 443}
    es_client = Elasticsearch(
        [ctx.elastic_search.host],
        http_auth=(ctx.elastic_search.username, ctx.secrets.elastic_search.password),
        http_compress=True,
        **protocol_config
    )
    # test if it works
    if not silent and not es_client.cat.health(request_timeout=30):
        raise ValueError('Credentials do not work for Elastic search')
    return es_client


@task()
def setup(ctx):
    client = get_es_client(ctx)
    client.snapshot.create_repository("backups", verify=True, body={
        "type": "fs",
        "settings": {
            "location": "backups"
        }
    })


@task
def create_snapshot(ctx, name):
    client = get_es_client(ctx)
    client.snapshot.create(repository="backups", snapshot=name, wait_for_completion=True)


@task
def load_repository(ctx, file_name):
    repositories_directory = os.path.join("elastic", "repositories")
    local_repository_file = os.path.join(repositories_directory, file_name)
    if not os.path.exists(local_repository_file):
        ctx.run(f"aws s3 cp s3://edushare-data/elastic/{file_name} {local_repository_file}", echo=True)
    ctx.run(f"unzip {local_repository_file} -d {repositories_directory}", echo=True)


@task
def restore_snapshot(ctx, name):
    client = get_es_client(ctx)
    client.indices.delete("_all", allow_no_indices=True, ignore_unavailable=True)
    client.snapshot.restore(repository="backups", snapshot=name, wait_for_completion=True, request_timeout=300)
