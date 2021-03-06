from dateutil.parser import parse
from datetime import datetime

from django.conf import settings

from surf.vendor.elasticsearch.api import ElasticSearchApiClient
from e2e_tests.base import BaseElasticSearchTestCase
from e2e_tests.elasticsearch_fixtures.elasticsearch import generate_nl_material


class TestsElasticSearch(BaseElasticSearchTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        math_and_education_disciplines = [
            "7afbb7a6-c29b-425c-9c59-6f79c845f5f0",  # math
            "0861c43d-1874-4788-b522-df8be575677f"  # onderwijskunde
        ]
        biology_disciplines = [
            "2b363227-8633-4652-ad57-c61f1efc02c8"
        ]
        biology_and_education_disciplines = biology_disciplines + [
            "0861c43d-1874-4788-b522-df8be575677f"
        ]

        cls.instance = ElasticSearchApiClient()
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["HBO"], file_type="text", source="surf",
                                      disciplines=math_and_education_disciplines),
        )
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["HBO"], file_type="text", source="surf", copyright="cc-by-40",
                                      topic="biology", publisher_date="2018-04-16T22:35:09+02:00",
                                      disciplines=biology_and_education_disciplines),
        )
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["HBO"], file_type="pdf", source="surf", topic="biology",
                                      publisher_date="2019-04-16T22:35:09+02:00",
                                      disciplines=biology_and_education_disciplines),
        )
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["HBO"], file_type="video", source="surf", topic="biology",
                                      disciplines=biology_disciplines),
            refresh=True  # always put refresh on the last material
        )

    def test_basic_search(self):
        search_result = self.instance.search('')
        search_result_filter = self.instance.search(
            '', filters=[{"external_id": "lom.technical.format", "items": ["video"]}])
        # did we get _anything_ from search?
        self.assertIsNotNone(search_result)
        self.assertIsNotNone(search_result_filter)
        self.assertGreater(search_result['recordcount'], search_result_filter['recordcount'])
        self.assertEqual(set(search_result.keys()), {"recordcount", "records", "drilldowns", "did_you_mean"})
        # check if record count is an actual number
        # Edurep returns everything and Elastic nothing with an empty search
        self.assertIsInstance(search_result['recordcount'], int)
        # does an empty search return a list of records?
        self.assertIsInstance(search_result['records'], list)
        # are there no drilldowns for an empty search?
        self.assertIsInstance(search_result['drilldowns'], list)
        self.assertEqual(len(search_result['drilldowns']), 0)

        # basic search
        search_biologie = self.instance.search("biologie")
        self.assertIsNotNone(search_biologie)
        self.assertTrue(search_biologie["records"])
        self.assertIsNot(search_result, search_biologie)
        self.assertNotEqual(search_result['recordcount'], search_biologie['recordcount'])

        # basic search pagination
        search_page_1 = self.instance.search("", page_size=1)
        self.assertIsNotNone(search_page_1)
        self.assertNotEqual(search_page_1, search_result)
        search_page_2 = self.instance.search("", page=2, page_size=1)
        self.assertIsNotNone(search_page_2)
        self.assertNotEqual(search_page_2, search_page_1)

    def test_filter_search(self):
        # search with single filter applied
        search_biologie_video = self.instance.search(
            "biologie",
            filters=[{"external_id": "lom.technical.format", "items": ["video"]}]
        )
        self.assertTrue(search_biologie_video["records"])
        for record in search_biologie_video["records"]:
            self.assertEqual(record["format"], "video")
        search_biologie_video_and_pdf = self.instance.search(
            "biologie",
            filters=[{"external_id": "lom.technical.format", "items": ["video", "pdf"]}]
        )
        self.assertGreater(len(search_biologie_video_and_pdf["records"]), len(search_biologie_video["records"]))
        for record in search_biologie_video_and_pdf["records"]:
            self.assertIn(record["format"], ["video", "pdf"])

        # search with multiple filters applied
        search_biologie_text_and_cc_by = self.instance.search(
            "biologie",
            filters=[
                {"external_id": "lom.technical.format", "items": ["text"]},
                {"external_id": "lom.rights.copyrightandotherrestrictions", "items": ["cc-by-40"]}
            ]
        )
        self.assertTrue(search_biologie_text_and_cc_by["records"])
        for record in search_biologie_text_and_cc_by["records"]:
            self.assertEqual(record["format"], "text")
            self.assertEqual(record["copyright"], "cc-by-40")

        # AND search with multiple filters applied
        search_biologie_and_didactiek = self.instance.search("biologie didactiek")
        search_biologie_and_didactiek_with_filters = self.instance.search(
            "biologie didactiek",
            filters=[
                {"external_id": "lom.technical.format", "items": ["text"]},
                {"external_id": "lom.rights.copyrightandotherrestrictions", "items": ["cc-by-40"]}
            ])

        self.assertIsNotNone(search_biologie_and_didactiek)
        self.assertTrue(search_biologie_and_didactiek["records"])
        self.assertIsNot(search_biologie_and_didactiek, search_biologie_and_didactiek_with_filters)
        self.assertTrue(search_biologie_and_didactiek_with_filters["records"])
        self.assertNotEqual(
            search_biologie_and_didactiek['recordcount'],
            search_biologie_and_didactiek_with_filters['recordcount']
        )

        # search with publish date filter applied
        search_biologie_upper_date = self.instance.search("biologie", filters=[
            {"external_id": "lom.lifecycle.contribute.publisherdate", "items": [None, "2018-12-31"]}
        ])
        self.assertTrue(search_biologie_upper_date["records"])
        for record in search_biologie_upper_date["records"]:
            publish_date = parse(record["publish_datetime"], ignoretz=True)
            self.assertLessEqual(publish_date, datetime.strptime("2018-12-31", "%Y-%m-%d"))
        search_biologie_lower_date = self.instance.search("biologie", filters=[
            {"external_id": "lom.lifecycle.contribute.publisherdate", "items": ["2018-01-01", None]}
        ])
        self.assertTrue(search_biologie_lower_date["records"])
        for record in search_biologie_lower_date["records"]:
            publish_date = parse(record["publish_datetime"], ignoretz=True)
            self.assertGreaterEqual(publish_date, datetime.strptime("2018-01-01", "%Y-%m-%d"))
        search_biologie_between_date = self.instance.search("biologie", filters=[
            {"external_id": "lom.lifecycle.contribute.publisherdate", "items": ["2018-01-01", "2018-12-31"]}
        ])
        self.assertTrue(search_biologie_between_date["records"])
        for record in search_biologie_between_date["records"]:
            publish_date = parse(record["publish_datetime"], ignoretz=True)
            self.assertLessEqual(publish_date, datetime.strptime("2018-12-31", "%Y-%m-%d"))
            self.assertGreaterEqual(publish_date, datetime.strptime("2018-01-01", "%Y-%m-%d"))

        # search with None, None as date filter. This search should give the same result as not filtering at all.
        search_biologie_none_date = self.instance.search("biologie", filters=[
            {"external_id": "lom.lifecycle.contribute.publisherdate", "items": [None, None]}
        ])
        search_biologie = self.instance.search("biologie")
        self.assertEqual(search_biologie_none_date, search_biologie)

    def test_search_disciplines(self):
        search_result = self.instance.search('')
        search_result_filter_1 = self.instance.search(
            '',
            filters=[{
                "external_id": "lom.classification.obk.discipline.id",
                "items": ['0861c43d-1874-4788-b522-df8be575677f']
            }]
        )
        search_result_filter_2 = self.instance.search(
            '',
            filters=[{
                "external_id": "lom.classification.obk.discipline.id",
                "items": ['2b363227-8633-4652-ad57-c61f1efc02c8']
            }]
        )
        search_result_filter_3 = self.instance.search(
            '',
            filters=[{
                "external_id": "lom.classification.obk.discipline.id",
                "items": ['0861c43d-1874-4788-b522-df8be575677f', '2b363227-8633-4652-ad57-c61f1efc02c8']
            }]
        )
        self.assertNotEqual(search_result, search_result_filter_1)
        self.assertNotEqual(search_result, search_result_filter_2)
        self.assertNotEqual(search_result_filter_1, search_result_filter_2)
        self.assertGreater(search_result['recordcount'], 0)
        self.assertGreater(search_result_filter_1['recordcount'], 0)
        self.assertGreater(search_result_filter_2['recordcount'], 0)
        self.assertGreater(
            search_result_filter_1['recordcount'] + search_result_filter_2['recordcount'],
            search_result_filter_3['recordcount'],
            "Expected at least 1 material to appear in both search_result_filter_1 and search_result_filter_2, "
            "which would make the sum of those results larger than filtering on both disciplines together"
        )

    def test_drilldown_search(self):
        search_biologie = self.instance.search("biologie", drilldown_names=["lom.technical.format"])
        self.assertIsNotNone(search_biologie)
        self.assertTrue(search_biologie['drilldowns'])
        self.assertTrue(search_biologie['drilldowns'][0]['items'])
        for item in search_biologie['drilldowns'][0]['items']:
            self.assertTrue(item['external_id'])
            self.assertIsNotNone(item['count'])

        search_with_theme_drilldown = self.instance.search(
            '',
            drilldown_names=["lom.classification.obk.discipline.id"]
        )
        self.assertIsNotNone(search_with_theme_drilldown)
        self.assertTrue(search_with_theme_drilldown['drilldowns'])
        self.assertEqual(
            [drilldown["external_id"] for drilldown in search_with_theme_drilldown['drilldowns']],
            ["lom.classification.obk.discipline.id"]
        )
        for drilldown in search_with_theme_drilldown['drilldowns']:
            self.assertTrue(drilldown["items"])
            for item in drilldown['items']:
                self.assertTrue(item['external_id'])
                self.assertIsNotNone(item['count'])

    def test_drilldown_with_filters(self):
        search = self.instance.search(
            "biologie",
            filters=[
                {"external_id": "lom.technical.format", "items": ["text"]}
            ],
            drilldown_names=['about.repository', 'lom.educational.context', 'lom.technical.format']
        )

        drilldowns = search['drilldowns']
        drilldowns_for_format = next((d for d in drilldowns if d['external_id'] == 'lom.technical.format'), None)
        drilldowns_for_repo = next((d for d in drilldowns if d['external_id'] == 'about.repository'), None)

        total_for_format = sum(item['count'] for item in drilldowns_for_format['items'])
        total_for_repo = sum(item['count'] for item in drilldowns_for_repo['items'])

        # The counts for format do not include the filter (as it is applied to format)
        # The counts for repo DO include the format filter, so it returns less results
        self.assertGreater(total_for_format, total_for_repo)

    def test_ordering_search(self):
        # make a bunch of queries with different ordering
        search_biologie = self.instance.search("biologie")
        self.assertIsNotNone(search_biologie)
        self.assertTrue(search_biologie["records"])
        search_biologie_dates = [record["publish_datetime"] for record in search_biologie["records"]]
        search_biologie_asc = self.instance.search("biologie", ordering="lom.lifecycle.contribute.publisherdate")
        self.assertIsNotNone(search_biologie_asc)
        self.assertTrue(search_biologie_asc["records"])
        search_biologie_asc_dates = [record["publish_datetime"] for record in search_biologie_asc["records"]]
        search_biologie_desc = self.instance.search("biologie", ordering="lom.lifecycle.contribute.publisherdate")
        self.assertIsNotNone(search_biologie_desc)
        self.assertTrue(search_biologie_asc["records"])
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
        biologie_autocomplete = self.instance.autocomplete(query='bio')
        self.assertGreater(len(biologie_autocomplete), 0)
        self.assertIsNot(empty_autocomplete, biologie_autocomplete)
        self.assertIsInstance(biologie_autocomplete, list)
        for item in biologie_autocomplete:
            self.assertIsInstance(item, str)
            self.assertTrue('biologie' in item)

    def test_drilldowns(self):
        empty_drilldowns = self.instance.drilldowns(drilldown_names=[])
        self.assertGreater(empty_drilldowns['recordcount'], 0)
        self.assertFalse(empty_drilldowns['records'])
        self.assertFalse(empty_drilldowns['drilldowns'])

        biologie_drilldowns = self.instance.drilldowns([], search_text="biologie")
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

        test_id = 'surf:oai:surfsharekit.nl:3522b79c-928c-4249-a7f7-d2bcb3077f10'
        result = self.instance.get_materials_by_id(external_ids=[test_id])
        self.assertIsNotNone(result)
        # we're searching for one id, we should get only one result
        self.assertEqual(result['recordcount'], 1)
        material = result['records'][0]

        self.assertEqual(material['title'], 'Didactiek van wiskundig denken')
        self.assertEqual(
            material['url'],
            "https://maken.wikiwijs.nl/91192/Wiskundedidactiek_en_ICT"
        )
        self.assertEqual(material['external_id'], test_id)
        self.assertEqual(material['publishers'], ["Wikiwijs Maken"])
        self.assertEqual(material['publish_datetime'], "2017-04-16T22:35:09+02:00")
        self.assertEqual(material['authors'], ["Michel van Ast", "Theo van den Bogaart", "Marc de Graaf"])
        self.assertEqual(material['keywords'], ["nerds"])
        self.assertEqual(material['disciplines'], [
            "7afbb7a6-c29b-425c-9c59-6f79c845f5f0",  # math
            "0861c43d-1874-4788-b522-df8be575677f"  # onderwijskunde
        ])
        self.assertEqual(material['language'], 'nl')
        self.assertEqual(material['format'], 'text')

    def test_search_by_author(self):
        author = "Michel van Ast"
        expected_record_count = 4
        self.check_author_search(author, expected_record_count)

        author2 = "Theo van den Bogaart"
        expected_record_count2 = 1
        self.check_author_search(author2, expected_record_count2)

    def check_author_search(self, author, expected_record_count):
        search_author = self.instance.search(
            '',
            filters=[{"external_id": "lom.lifecycle.contribute.author", "items": [author]}]
        )
        for record in search_author['records']:
            self.assertIn(author, record['authors'])
        self.assertEqual(search_author['recordcount'], expected_record_count)

    def test_search_did_you_mean(self):
        spelling_mistake = self.instance.search('didaktiek')
        self.assertIn("did_you_mean", spelling_mistake)
        self.assertEqual(spelling_mistake["did_you_mean"]["original"], "didaktiek")
        self.assertEqual(spelling_mistake["did_you_mean"]["suggestion"], "didactiek")
        no_result_spelling_mistake = self.instance.search('didaktiek is fantastiek')
        self.assertEqual(no_result_spelling_mistake["did_you_mean"], {})
        no_mistake = self.instance.search('biologie')
        self.assertEqual(no_mistake["did_you_mean"], {})
        unknown_mistake = self.instance.search('sdfkhjsdgaqegkjwfgklsd')
        self.assertEqual(unknown_mistake["did_you_mean"], {})
