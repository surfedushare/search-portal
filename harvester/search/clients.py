from opensearchpy import OpenSearch, RequestsHttpConnection

from django.conf import settings

from search_client import SearchClient


def get_search_client(document_type=None, alias_prefix=None):
    document_type = document_type or settings.DOCUMENT_TYPE
    kwargs = {}
    if "amazonaws.com" in settings.OPENSEARCH_HOST:
        kwargs["basic_auth"] = ("supersurf", settings.OPENSEARCH_PASSWORD,)
        kwargs["verify_certs"] = settings.OPENSEARCH_VERIFY_CERTS
    return SearchClient(
        settings.OPENSEARCH_HOST,
        document_type,
        alias_prefix if alias_prefix else settings.OPENSEARCH_ALIAS_PREFIX,
        search_results_key="results",
        **kwargs
    )


def get_opensearch_client():

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
