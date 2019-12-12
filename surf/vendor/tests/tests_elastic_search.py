from surf.vendor.elasticsearch.api import ElasticSearchApiClient
from .base import get_base_search_test_class


class ElasticSearchTestCase(get_base_search_test_class()):
    test_class = ElasticSearchApiClient
