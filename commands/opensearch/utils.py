from opensearchpy import OpenSearch, RequestsHttpConnection


def get_remote_search_client(conn, silent=False):
    """
    Returns the Open Search client connected through port forwarding settings
    """
    host = conn.config.opensearch.host
    protocol_config = {
        "scheme": "https",
        "port": 443,
        "use_ssl": True,
        "verify_certs": True,
    }

    http_auth = ("supersurf", conn.config.secrets.opensearch.password,)

    es_client = OpenSearch(
        [host],
        http_auth=http_auth,
        connection_class=RequestsHttpConnection,
        **protocol_config
    )

    # test if it works
    if not silent and not es_client.cat.health(request_timeout=30):
        raise ValueError('Credentials do not work for Open Search')
    return es_client
