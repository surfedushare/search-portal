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
    import ipdb; ipdb.set_trace()
