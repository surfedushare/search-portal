from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3


def get_es_client(conn, silent=False):
    """
    Returns the elasticsearch client connected through port forwarding settings
    """
    elastic_url = "https://localhost:9222"
    protocol_config = {
        "scheme": "https",
        "port": 9222,
        "use_ssl": True,
        "verify_certs": False,
    }
    credentials = boto3.Session(profile_name=conn.aws.profile_name).get_credentials()
    http_auth = AWS4Auth(credentials.access_key, credentials.secret_key, "eu-central-1", "es",
                         session_token=credentials.token)

    es_client = Elasticsearch(
        [elastic_url],
        http_auth=http_auth,
        connection_class=RequestsHttpConnection,
        **protocol_config
    )

    # test if it works
    if not silent and not es_client.cat.health(request_timeout=30):
        raise ValueError('Credentials do not work for Elastic search')
    return es_client
