from elasticsearch import Elasticsearch

from django.conf import settings


def get_es_client():
    elastic_url = settings.ELASTICSEARCH_HOST
    protocol = settings.ELASTICSEARCH_PROTOCOL
    protocol_config = {} if protocol == "http" else {"scheme": "https", "port": 443}
    return Elasticsearch(
        [elastic_url],
        http_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD),
        **protocol_config
    )
