from django.conf import settings
from django.test import TestCase
from surf.vendor.edurep.xml_endpoint.v1_2.api import XmlEndpointApiClient
from surf.vendor.elasticsearch.api import ElasticSearchApiClient


class BaseSearchTestCase(TestCase):
    test_class = ElasticSearchApiClient

    def setUp(self):
        # both the elastic and the edurep classes have a default base paramter so don't change it if we don't need to
        self.instance = self.test_class()

    def test_search(self):
        search_result = self.instance.search("")
        # did we get _anything_ from search?
        self.assertIsNotNone(search_result)
        # is the total number of searchablen items > 0
        # if this is 0 there must be something wrong with the search engine (might not be our problem)
        self.assertTrue(search_result['recordcount'] > 0)
        # does an empty search return records?
        self.assertGreater(len(search_result['records']), 0)
        # are there no drilldowns for an empty search?
        self.assertEqual(len(search_result['drilldowns']), 0)

        search_biologie = self.instance.search("biologie")
        self.assertIsNotNone(search_biologie)
        self.assertIsNot(search_result, search_biologie)
        self.assertGreater(search_result['recordcount'], search_biologie['recordcount'])

        search_biologie_2 = self.instance.search("biologie", page=2)
        self.assertIsNotNone(search_biologie_2)
        self.assertIsNot(search_biologie_2, search_biologie)

    def test_autocomplete(self):
        empty_autocomplete = self.instance.autocomplete(query='')
        self.assertEqual(len(empty_autocomplete), 0)

        biologie_autocomplete = self.instance.autocomplete(query='biologie')
        self.assertGreater(len(biologie_autocomplete), 0)
        self.assertIsNot(empty_autocomplete, biologie_autocomplete)
        self.assertIsInstance(biologie_autocomplete, list)
        for item in biologie_autocomplete:
            self.assertIsInstance(item, str)
            self.assertTrue('biologie' in item)

    def test_drilldowns(self):
        empty_drilldowns = self.instance.drilldowns(drilldown_names=[])
        #{'recordcount': 1298193, 'records': [], 'drilldowns': []}
        self.assertGreater(empty_drilldowns['recordcount'], 0)
        self.assertFalse(empty_drilldowns['records'])
        self.assertFalse(empty_drilldowns['drilldowns'])

        biologie_drilldowns = self.instance.drilldowns([], search_text="biologie")
        #{'recordcount': 32, 'records': [], 'drilldowns': []}
        self.assertGreater(biologie_drilldowns['recordcount'], 0)
        self.assertGreater(empty_drilldowns['recordcount'], biologie_drilldowns['recordcount'])
        self.assertFalse(biologie_drilldowns['records'])
        self.assertFalse(biologie_drilldowns['drilldowns'])

        repo_drilldowns = self.instance.drilldowns(['about.repository'])
        self.assertTrue(repo_drilldowns['drilldowns'])
        self.assertTrue(repo_drilldowns['drilldowns'][0]['items'])
        for item in repo_drilldowns['drilldowns'][0]['items']:
            self.assertTrue(item['external_id'])
            self.assertIsNotNone(item['count'])

    def test_get_materials_by_id(self):
        def test_material(external_id):
            # can't test for theme and copyright without creating and instantiating these values in the database
            material_keys = ['object_id', 'url', 'title', 'description', 'keywords', 'language', 'aggregationlevel',
                             'publisher', 'publish_datetime', 'author', 'format', 'disciplines', 'educationallevels']

            material = self.instance.get_materials_by_id(external_ids=[external_id])

            self.assertIsNotNone(material)
            # we're searching for one id, we should get only one result
            self.assertEqual(material['recordcount'], 1)

            material = material['records'][0]
            for key in material_keys:
                self.assertIsNotNone(material[key])
            return material

        material_1 = test_material('wikiwijsmaken:44170')
        material_2 = test_material('wikiwijsmaken:137024')

        self.assertIsNot(material_1, material_2)

        self.assertEqual(material_1['title'], 'Wiskundeformules in een Wikiwijs-arrangement')
        self.assertEqual(material_1['url'], 'http://maken.wikiwijs.nl/44170/Wiskundeformules_in_een_Wikiwijs_arrangement')
        self.assertEqual(material_1['object_id'], 'urn:wikiwijsmaken:44170')
        self.assertEqual(material_1['publisher'], 'Wikiwijs Maken')
        self.assertEqual(material_1['creator'], 'Wikiwijs Maken')
        self.assertEqual(material_1['publish_datetime'], '2013-04-19T23:00:41+02:00')
        self.assertEqual(material_1['author'], 'Marc van Maastricht')
        self.assertEqual(material_1['number_of_collections'], 0)
        self.assertEqual(len(material_1['educationallevels']), 49)
        self.assertEqual(len(material_1['disciplines']), 9)

        self.assertEqual(material_2['object_id'], 'urn:wikiwijsmaken:137024')
        self.assertEqual(material_2['url'], 'https://maken.wikiwijs.nl/137024/Themales_1_Wessel_Poot')
        self.assertEqual(material_2['title'], 'Themales 1 Wessel Poot')
        self.assertEqual(material_2['keywords'], ['aardrijkskunde', 'adl'])
        self.assertEqual(material_2['language'], 'nl')
        self.assertIsNone(material_2['copyright'])
        self.assertEqual(material_2['publisher'], 'Wikiwijs Maken')
        self.assertEqual(material_2['author'], 'Wessel Poot')
        self.assertEqual(material_2['creator'], 'Wikiwijs Maken')
        self.assertEqual(material_2['format'], 'wikiwijsarrangement')
