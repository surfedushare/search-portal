from django.conf import settings

from search_client import SearchClient, DocumentTypes


def get_search_client(alias_prefix=None):
    kwargs = {}
    if "amazonaws.com" in settings.OPENSEARCH_HOST:
        kwargs["basic_auth"] = ("supersurf", settings.OPENSEARCH_PASSWORD,)
        kwargs["verify_certs"] = settings.OPENSEARCH_VERIFY_CERTS
    return SearchClient(
        settings.OPENSEARCH_HOST,
        DocumentTypes.LEARNING_MATERIAL,
        alias_prefix if alias_prefix else settings.OPENSEARCH_ALIAS_PREFIX,
        **kwargs
    )
