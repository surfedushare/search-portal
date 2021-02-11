from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from django.conf import settings
from django.test import override_settings, TestCase

from elasticsearch import Elasticsearch

from surfpol.configuration import create_elastic_search_index_configuration


class BaseElasticSearchMixin(object):

    @classmethod
    def index_body(cls, language):
        analyzer = 'dutch' if language == 'nl' else 'english'
        decompound_word_list = "decompound_word_list.nl.txt" if language == "nl" else None
        return create_elastic_search_index_configuration(language, analyzer, decompound_word_list=decompound_word_list)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.elastic = Elasticsearch(
            [settings.ELASTICSEARCH_HOST]
        )
        cls.elastic.indices.create(settings.ELASTICSEARCH_NL_INDEX, ignore=400, body=cls.index_body('nl'))
        cls.elastic.indices.create(settings.ELASTICSEARCH_EN_INDEX, ignore=400, body=cls.index_body('en'))

    @classmethod
    def tearDownClass(cls):
        cls.elastic.indices.delete(settings.ELASTICSEARCH_NL_INDEX)
        cls.elastic.indices.delete(settings.ELASTICSEARCH_EN_INDEX)


@override_settings(ELASTICSEARCH_NL_INDEX="test-nl", ELASTICSEARCH_EN_INDEX="test-en")
class BaseLiveServerTestCase(BaseElasticSearchMixin, StaticLiveServerTestCase):

    fixtures = ['locales', 'filter-categories', 'privacy_statements']

    def setUp(self):
        super().setUp()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("window-size=1920,1080")

        self.selenium = WebDriver(options=chrome_options)
        self.selenium.implicitly_wait(10)

    def tearDown(self):
        super().tearDown()
        self.selenium.quit()


@override_settings(ELASTICSEARCH_NL_INDEX="test-nl", ELASTICSEARCH_EN_INDEX="test-en")
class BaseElasticSearchTestCase(BaseElasticSearchMixin, TestCase):

    fixtures = ['locales', 'filter-categories', 'privacy_statements']
