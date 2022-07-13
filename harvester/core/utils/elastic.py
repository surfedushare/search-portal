from opensearchpy import OpenSearch, RequestsHttpConnection

from django.conf import settings


def get_es_client():

    elastic_url = settings.ELASTICSEARCH_HOST
    protocol = settings.ELASTICSEARCH_PROTOCOL
    protocol_config = {}
    if protocol == "https":
        protocol_config = {
            "scheme": "https",
            "port": 443,
            "use_ssl": True,
            "verify_certs": settings.ELASTICSEARCH_VERIFY_CERTS,
        }

    if settings.IS_AWS:
        http_auth = ("supersurf", settings.OPENSEARCH_PASSWORD)
    else:
        http_auth = (None, None)

    return OpenSearch(
        [elastic_url],
        http_auth=http_auth,
        connection_class=RequestsHttpConnection,
        **protocol_config
    )
