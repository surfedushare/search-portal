from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, override_settings
from opensearchpy import OpenSearch
from project.configuration import create_open_search_index_configuration
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class BaseOpenSearchMixin(object):

    @classmethod
    def index_body(cls, language):
        return create_open_search_index_configuration(language)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.search = OpenSearch(
            [settings.OPENSEARCH_HOST]
        )
        cls.search.indices.create(settings.OPENSEARCH_NL_INDEX, ignore=400, body=cls.index_body('nl'))
        cls.search.indices.create(settings.OPENSEARCH_EN_INDEX, ignore=400, body=cls.index_body('en'))
        cls.search.indices.create(settings.OPENSEARCH_UNK_INDEX, ignore=400, body=cls.index_body('unk'))

    @classmethod
    def tearDownClass(cls):
        cls.search.indices.delete(settings.OPENSEARCH_NL_INDEX)
        cls.search.indices.delete(settings.OPENSEARCH_EN_INDEX)
        cls.search.indices.delete(settings.OPENSEARCH_UNK_INDEX)
        super().tearDownClass()


@override_settings(
    OPENSEARCH_NL_INDEX="test-nl",
    OPENSEARCH_EN_INDEX="test-en",
    OPENSEARCH_UNK_INDEX="test-unk"
)
class BaseLiveServerTestCase(BaseOpenSearchMixin, StaticLiveServerTestCase):

    fixtures = ['locales-edusources', 'privacy_statements']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("window-size=1920,1080")

        cls.selenium = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        cls.selenium.implicitly_wait(10)
        cls.explicit_wait = 300

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()


@override_settings(
    OPENSEARCH_NL_INDEX="test-nl",
    OPENSEARCH_EN_INDEX="test-en",
    OPENSEARCH_UNK_INDEX="test-unk"
)
class BaseOpenSearchTestCase(BaseOpenSearchMixin, TestCase):

    fixtures = ['locales-edusources', 'privacy_statements']
