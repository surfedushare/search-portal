from opensearchpy import OpenSearch, RequestsHttpConnection


def get_search_client(conn, silent=False):
    """
    Returns the elasticsearch client connected through port forwarding settings
    """
    elastic_url = conn.config.open_search.host
    protocol_config = {
        "scheme": "https",
        "port": 443,
        "use_ssl": True,
        "verify_certs": True,
    }

    http_auth = ("supersurf", conn.config.secrets.opensearch.password,)

    es_client = OpenSearch(
        [elastic_url],
        http_auth=http_auth,
        connection_class=RequestsHttpConnection,
        **protocol_config
    )

    # test if it works
    if not silent and not es_client.cat.health(request_timeout=30):
        raise ValueError('Credentials do not work for Elastic search')
    return es_client
