from django.conf import settings

from surf.vendor.edurep.xml_endpoint.v1_2.api import XmlEndpointApiClient
from surf.vendor.elasticsearch.api import ElasticSearchApiClient


def get_search_client():
    client_type = settings.SEARCH_CLIENT
    if client_type == 'elastic':
        return ElasticSearchApiClient()
    if client_type == 'edurep':
        return XmlEndpointApiClient()
