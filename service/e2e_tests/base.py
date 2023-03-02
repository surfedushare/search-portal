from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from opensearchpy import OpenSearch

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase

from search_client import SearchClient
from search_client.constants import LANGUAGES, DocumentTypes
from search_client.open_search.configuration import create_open_search_index_configuration


class BaseLiveServerTestCase(StaticLiveServerTestCase):

    selenium = None
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


class BaseOpenSearchTestCase(TestCase):

    search = None
    instance = None
    alias_prefix = None

    @classmethod
    def index_body(cls, language):
        return create_open_search_index_configuration(language, DocumentTypes.LEARNING_MATERIAL)

    @classmethod
    def get_alias(cls, language):
        return f"{cls.alias_prefix}-{language}"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.search = OpenSearch(
            [settings.OPENSEARCH_HOST]
        )
        for language in LANGUAGES:
            cls.search.indices.create(
                cls.get_alias(language),
                ignore=400,
                body=cls.index_body('nl')
            )
        cls.instance = SearchClient(
            f"{settings.PROTOCOL}://{settings.OPENSEARCH_HOST}",
            DocumentTypes.LEARNING_MATERIAL,
            cls.alias_prefix
        )

    @classmethod
    def tearDownClass(cls):
        for language in LANGUAGES:
            cls.search.indices.delete(
                cls.get_alias(language)
            )
        cls.search.close()
        cls.instance.client.close()
        super().tearDownClass()

    fixtures = ['locales-edusources', 'privacy_statements']
