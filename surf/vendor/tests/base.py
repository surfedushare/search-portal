from django.test import TestCase


class BaseSearchTestCase(TestCase):
    test_class = None

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
            material_keys = ['object_id', 'url', 'title', 'description', 'keywords', 'language',
                             'publish_datetime', 'author', 'format', 'disciplines', 'educationallevels']

            result = self.instance.get_materials_by_id(external_ids=[external_id])

            self.assertIsNotNone(result)
            # we're searching for one id, we should get only one result
            self.assertEqual(result['recordcount'], 1)

            material = result['records'][0]
            # for key in material_keys:
            #     print(key)
            #     self.assertIsNotNone(material[key])
            return material
        test_id_1 = 'metaplus:vilentum:oai:www.samhao.nl:VBS:2:144126'
        test_id_2 = 'edurep_delen:c4443aed-83ac-4182-829f-50f86b0c0124'
        material_1 = test_material(test_id_1)
        material_2 = test_material(test_id_2)

        self.assertIsNot(material_1, material_2)

        self.assertEqual(material_1['title'], 'Ruwvoer en kaaskwaliteit')
        self.assertEqual(material_1['url'], 'http://www.samhao.nl/webopac/MetaDataEditDownload.csp?file=2:144126:1')
        self.assertEqual(material_1['object_id'], test_id_1)
        self.assertEqual(material_1['publish_datetime'], '2018')
        self.assertEqual(material_1['author'], ['BEGIN:VCARD\nVERSION: 3.0\nFN:Groot, R.\nN:Groot; R.\nEND:VCARD'])
        self.assertEqual(len(material_1['educationallevels']), 3)
        self.assertEqual(len(material_1['disciplines']), 1)

        self.assertEqual(material_2['title'], 'Een kind wil aardige en geen gemene getallen')
        self.assertEqual(material_2['url'], 'http://thomascool.eu/Papers/AardigeGetallen/Index.html')
        self.assertEqual(material_2['object_id'], test_id_2)
        self.assertEqual(material_2['keywords'], ['rekenen', 'uitspraak getallen', 'wiskunde', 'meetkunde', 'breuken', 'verhoudingen', 'lijnen', 'functies', 'parlement'])
        self.assertEqual(material_2['language'], 'nl')
        self.assertEqual(material_2['author'], [])
        self.assertEqual(material_2['format'], 'video')


def get_base_search_test_class():
    return BaseSearchTestCase
