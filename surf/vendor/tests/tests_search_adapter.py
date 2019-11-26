from django.conf import settings
from django.test import TestCase
from surf.vendor.edurep.xml_endpoint.v1_2.api import XmlEndpointApiClient


class BaseSearchTestCase(TestCase):
    test_class = XmlEndpointApiClient

    def setUp(self):
        self.instance = self.test_class(settings.EDUREP_XML_API_ENDPOINT)

    def empty_search_test(self):
        search_result = self.instance.search("")
        # did we get _anything_ from search?
        self.assertIsNotNone(search_result)
        # is the total number of searchablen items > 0
        self.assertTrue(search_result['recordcount'] > 0)
        # does an empty search return records?
        self.assertTrue(len(search_result['records']) > 0)
        # are there no drilldowns for an empty search?
        self.assertTrue(len(search_result['drilldowns']) == 0)
