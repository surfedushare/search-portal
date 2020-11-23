from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

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

    if settings.ELASTICSEARCH_IS_AWS:
        credentials = boto3.Session().get_credentials()
        http_auth = AWS4Auth(credentials.access_key, credentials.secret_key, "eu-central-1", "es",
                             session_token=credentials.token)
    else:
        http_auth = (None, None)

    return Elasticsearch(
        [elastic_url],
        http_auth=http_auth,
        connection_class=RequestsHttpConnection,
        **protocol_config
    )
