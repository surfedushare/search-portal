from unittest.mock import create_autospec

from elasticsearch.client import Elasticsearch, IndicesClient


def get_elastic_client_mock():
    elastic_client_mock = create_autospec(Elasticsearch, instance=True)
    elastic_client_mock.indices = create_autospec(IndicesClient, instance=True)
    #elastic_client_mock.
    #print(dir(elastic_client_mock.indices))
    return elastic_client_mock
