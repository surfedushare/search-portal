from opensearchpy import OpenSearch, RequestsHttpConnection

from django.conf import settings


def get_search_client():

    opensearch_url = settings.OPENSEARCH_HOST
    protocol_config = {}
    if opensearch_url.startswith("https"):
        protocol_config = {
            "scheme": "https",
            "port": 443,
            "use_ssl": True,
            "verify_certs": settings.OPENSEARCH_VERIFY_CERTS,
        }

    if settings.IS_AWS:
        http_auth = ("supersurf", settings.OPENSEARCH_PASSWORD)
    else:
        http_auth = (None, None)

    return OpenSearch(
        [opensearch_url],
        http_auth=http_auth,
        connection_class=RequestsHttpConnection,
        **protocol_config
    )
