from dateutil.parser import parse
from datetime import datetime

from django.test import TestCase


class BaseSearchTestCase(TestCase):
    test_class = None

    def setUp(self):
        # both the elastic and the edurep classes have a default base paramter so don't change it if we don't need to
        self.instance = self.test_class()

    def test_basic_search(self):
        search_result = self.instance.search([])
        search_result_filter = self.instance.search([], filters=[{"external_id": "lom.technical.format", "items": ["video"]}])
        # did we get _anything_ from search?
        self.assertIsNotNone(search_result)
        self.assertIsNotNone(search_result_filter)
        self.assertGreater(search_result['recordcount'], search_result_filter['recordcount'])
        self.assertEqual(set(search_result.keys()), {"recordcount", "records", "drilldowns"})
        # check if record count is an actual number
        # Edurep returns everything and Elastic nothing with an empty search
        self.assertIsInstance(search_result['recordcount'], int)
        # does an empty search return a list of records?
        self.assertIsInstance(search_result['records'], list)
        # are there no drilldowns for an empty search?
        self.assertIsInstance(search_result['drilldowns'], list)
        self.assertEqual(len(search_result['drilldowns']), 0)

        # basic search
        search_biologie = self.instance.search(["biologie"])
        self.assertIsNotNone(search_biologie)
        self.assertIsNot(search_result, search_biologie)
        self.assertNotEqual(search_result['recordcount'], search_biologie['recordcount'])

        # basic search second page
        search_biologie_2 = self.instance.search(["biologie"], page=2)
        self.assertIsNotNone(search_biologie_2)
        self.assertNotEqual(search_biologie_2, search_biologie)

    def test_filter_search(self):

        # search with single filter applied
        search_biologie_video = self.instance.search(
            ["biologie"],
            filters=[{"external_id": "lom.technical.format", "items": ["video"]}]
        )
        for record in search_biologie_video["records"]:
            self.assertEqual(record["format"], "video")
        search_biologie_video_and_pdf = self.instance.search(
            ["biologie"],
            filters=[{"external_id": "lom.technical.format", "items": ["video", "pdf"]}]
        )
        for record in search_biologie_video_and_pdf["records"]:
            self.assertIn(record["format"], ["video", "pdf"])

        # search with multiple filters applied
        search_biologie_text_and_cc_by = self.instance.search(
            ["biologie"],
            filters=[
                {"external_id": "lom.technical.format", "items": ["text"]},
                {"external_id": "lom.rights.copyrightandotherrestrictions", "items": ["cc-by"]}
            ]
        )
        for record in search_biologie_text_and_cc_by["records"]:
            self.assertEqual(record["format"], "text")
            self.assertEqual(record["copyright"], "cc-by-40")

        # AND search with multiple filters applied
        search_biologie_and_natuur = self.instance.search(["biologie", "natuur"])
        search_biologie_and_natuur_with_filters = self.instance.search(
            ["biologie", "natuur"],
            filters=[
                {"external_id": "lom.technical.format", "items": ["text"]},
                {"external_id": "lom.rights.copyrightandotherrestrictions", "items": ["cc-by"]}
            ])

        self.assertIsNotNone(search_biologie_and_natuur)
        self.assertIsNot(search_biologie_and_natuur, search_biologie_and_natuur_with_filters)
        self.assertNotEqual(
            search_biologie_and_natuur['recordcount'],
            search_biologie_and_natuur_with_filters['recordcount']
        )

        # search with publish date filter applied
        search_biologie_upper_date = self.instance.search(["biologie"], filters=[
            {"external_id": "lom.lifecycle.contribute.publisherdate", "items": [None, "2018-12-31"]}
        ])
        for record in search_biologie_upper_date["records"]:
            publish_date = parse(record["publish_datetime"], ignoretz=True)
            self.assertLessEqual(publish_date, datetime.strptime("2018-12-31", "%Y-%m-%d"))
        search_biologie_lower_date = self.instance.search(["biologie"], filters=[
            {"external_id": "lom.lifecycle.contribute.publisherdate", "items": ["2018-01-01", None]}
        ])
        for record in search_biologie_lower_date["records"]:
            publish_date = parse(record["publish_datetime"], ignoretz=True)
            self.assertGreaterEqual(publish_date, datetime.strptime("2018-01-01", "%Y-%m-%d"))
        search_biologie_between_date = self.instance.search(["biologie"], filters=[
            {"external_id": "lom.lifecycle.contribute.publisherdate", "items": ["2018-01-01", "2018-12-31"]}
        ])
        for record in search_biologie_between_date["records"]:
            publish_date = parse(record["publish_datetime"], ignoretz=True)
            self.assertLessEqual(publish_date, datetime.strptime("2018-12-31", "%Y-%m-%d"))
            self.assertGreaterEqual(publish_date, datetime.strptime("2018-01-01", "%Y-%m-%d"))

        # search with None, None as date filter. This search should give the same result as not filtering at all.
        search_biologie_none_date = self.instance.search(["biologie"], filters=[
            {"external_id": "lom.lifecycle.contribute.publisherdate", "items": [None, None]}
        ])
        search_biologie = self.instance.search(["biologie"])
        self.assertEqual(search_biologie_none_date, search_biologie)

    def test_search_disciplines(self):
        search_result = self.instance.search([])
        search_result_filter_1 = self.instance.search([], filters=[{"external_id": "lom.classification.obk.discipline.id", "items": ['2adcec22-095d-4937-aed7-48788080460b']}])
        search_result_filter_2 = self.instance.search([], filters=[{"external_id": "lom.classification.obk.discipline.id", "items": ['c001f86a-4f8f-4420-bd78-381c615ecedc']}])
        self.assertNotEqual(search_result, search_result_filter_1)
        self.assertNotEqual(search_result, search_result_filter_2)
        self.assertNotEqual(search_result_filter_1, search_result_filter_2)
        self.assertGreater(search_result['recordcount'], 0)
        self.assertGreater(search_result_filter_1['recordcount'], 0)
        self.assertGreater(search_result_filter_2['recordcount'], 0)

    def test_drilldown_search(self):
        search_biologie = self.instance.search(["biologie"], drilldown_names=["lom.technical.format"])
        self.assertIsNotNone(search_biologie)
        self.assertTrue(search_biologie['drilldowns'])
        self.assertTrue(search_biologie['drilldowns'][0]['items'])
        for item in search_biologie['drilldowns'][0]['items']:
            self.assertTrue(item['external_id'])
            self.assertIsNotNone(item['count'])

        search_with_theme_drilldown = self.instance.search(
            [],
            drilldown_names=["lom.classification.obk.discipline.id"]
        )
        self.assertIsNotNone(search_with_theme_drilldown)
        self.assertTrue(search_with_theme_drilldown['drilldowns'])
        self.assertEqual(
            [drilldown["external_id"] for drilldown in search_with_theme_drilldown['drilldowns']],
            ["lom.classification.obk.discipline.id", "custom_theme.id"]
        )
        for drilldown in search_with_theme_drilldown['drilldowns']:
            for item in drilldown['items']:
                self.assertTrue(item['external_id'])
                self.assertIsNotNone(item['count'])

    def test_ordering_search(self):
        # make a bunch of queries with different ordering
        search_biologie = self.instance.search(["biologie"])
        self.assertIsNotNone(search_biologie)
        search_biologie_dates = [record["publish_datetime"] for record in search_biologie["records"]]
        search_biologie_asc = self.instance.search(["biologie"], ordering="lom.lifecycle.contribute.publisherdate")
        self.assertIsNotNone(search_biologie_asc)
        search_biologie_asc_dates = [record["publish_datetime"] for record in search_biologie_asc["records"]]
        search_biologie_desc = self.instance.search(["biologie"], ordering="lom.lifecycle.contribute.publisherdate")
        self.assertIsNotNone(search_biologie_desc)
        search_biologie_desc_dates = [record["publish_datetime"] for record in search_biologie_desc["records"]]
        # make sure that a default ordering is different than a date ordering
        self.assertNotEqual(search_biologie_dates, search_biologie_asc_dates)
        self.assertNotEqual(search_biologie_dates, search_biologie_desc_dates)
        # make sure that the dates of results are indeed in expected order
        self.assertEqual(search_biologie_asc_dates, sorted(search_biologie_asc_dates))
        self.assertEqual(search_biologie_desc_dates, sorted(search_biologie_desc_dates, reverse=False))

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

        biologie_drilldowns = self.instance.drilldowns([], search_text=["biologie"])
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

        repo_and_format_drilldowns = self.instance.drilldowns(['about.repository', 'lom.technical.format'])
        self.assertTrue(repo_and_format_drilldowns['drilldowns'])
        for drilldown in repo_and_format_drilldowns['drilldowns']:
            self.assertTrue(drilldown['items'])
            for item in drilldown['items']:
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
        test_id_1 = 'surf:oai:surfsharekit.nl:bef89539-a037-454d-bee3-da09f4c94e0b'
        test_id_2 = 'edurep_delen:6e4447af-8ac3-4a91-a594-89828b068a2d'
        material_1 = test_material(test_id_1)
        material_2 = test_material(test_id_2)

        self.assertIsNot(material_1, material_2)

        self.assertEqual(material_1['title'], 'Decision Trees and Random Decision Forests')
        self.assertEqual(material_1['url'], 'https://surfsharekit.nl/dl/surf/bef89539-a037-454d-bee3-da09f4c94e0b/53c7bb36-e374-431c-a50c-e208ab53e412')
        self.assertEqual(material_1['external_id'], test_id_1)
        self.assertEqual(material_1['publish_datetime'], None)
        self.assertEqual(material_1['author'], None)
        self.assertEqual(material_1['keywords'], ['Powerpoint', 'Orange', 'MOOC'])
        self.assertEqual(len(material_1['educationallevels']), 2)
        self.assertEqual(len(material_1['disciplines']), 0)
        self.assertEqual(material_1['language'], 'en')
        self.assertEqual(material_1['format'], 'pdf')

        self.assertEqual(material_2['title'], 'Kennisclip herpes zoster')
        self.assertEqual(material_2['url'], 'https://delen.edurep.nl/download/6e4447af-8ac3-4a91-a594-89828b068a2d')
        self.assertEqual(material_2['external_id'], test_id_2)
        self.assertEqual(material_2['keywords'], ['#hbovpk', '#HR'])
        self.assertEqual(material_2['publish_datetime'], '2017-09-27T11:02:13+02:00')
        self.assertEqual(material_2['language'], 'nl')
        self.assertEqual(material_2['author'], 'Drs. E. Kuperi')
        self.assertEqual(len(material_2['themes']), 0)
        # TODO a bug in elasticsearch is messing this up:
        self.assertEqual(material_2['format'], 'pdf')


def get_base_search_test_class():
    return BaseSearchTestCase
