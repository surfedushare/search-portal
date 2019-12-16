from surf.vendor.edurep.xml_endpoint.v1_2.api import XmlEndpointApiClient
from .base import get_base_search_test_class


class EdurepSearchTestCase(get_base_search_test_class()):
    test_class = XmlEndpointApiClient
