from unittest.mock import create_autospec, Mock

from elasticsearch.client import Elasticsearch, IndicesClient


def get_elastic_client_mock(has_history=False):
    elastic_client_mock = create_autospec(Elasticsearch, instance=True)
    elastic_client_mock.indices = create_autospec(IndicesClient, instance=True)
    elastic_client_mock.indices.exists = Mock(return_value=has_history)
    return elastic_client_mock
