from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from django.db import connection

from elasticsearch import Elasticsearch
from django.conf import settings

class TestSearchEs(StaticLiveServerTestCase):
    fixtures = ['filter-categories', 'locales']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("window-size=1920,1080")

        cls.selenium = WebDriver(options=chrome_options)
        cls.selenium.implicitly_wait(10)
        cls.elastic = Elasticsearch(
            [settings.ELASTICSEARCH_HOST],
            http_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD)
        )
        mapping = '''
        {
            "mappings": {
                "_doc": {
                    "properties": {
                        "arrangement_collection_name": {
                            "type": "keyword"
                        },
                        "author": {
                            "type": "keyword"
                        },
                        "copyright": {
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            },
                            "type": "text"
                        },
                        "description": {
                            "analyzer": "dutch",
                            "type": "text"
                        },
                        "description_plain": {
                            "type": "text"
                        },
                        "disciplines": {
                            "type": "keyword"
                        },
                        "educational_levels": {
                            "type": "keyword"
                        },
                        "external_id": {
                            "type": "keyword"
                        },
                        "file_type": {
                            "type": "keyword"
                        },
                        "id": {
                            "type": "text"
                        },
                        "keywords": {
                            "type": "keyword"
                        },
                        "language": {
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            },
                            "type": "text"
                        },
                        "lom_educational_levels": {
                            "type": "keyword"
                        },
                        "mime_type": {
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            },
                            "type": "text"
                        },
                        "publisher_date": {
                            "type": "date"
                        },
                        "suggest": {
                            "analyzer": "simple",
                            "max_input_length": 50,
                            "preserve_position_increments": true,
                            "preserve_separators": true,
                            "type": "completion"
                        },
                        "text": {
                            "analyzer": "dutch",
                            "type": "text"
                        },
                        "text_plain": {
                            "type": "text"
                        },
                        "title": {
                            "analyzer": "dutch",
                            "type": "text"
                        },
                        "title_plain": {
                            "type": "text"
                        },
                        "transcription": {
                            "analyzer": "dutch",
                            "type": "text"
                        },
                        "transcription_plain": {
                            "type": "text"
                        },
                        "url": {
                            "type": "text"
                        }
                    }
                }
            }
        }

        '''
        cls.elastic.indices.create('test-nl', ignore=400, body=mapping)
        material = '''
        {
            "title": "Didactiek van wiskundig denken",
            "text": "Leermateriaal over wiskunde en didactiek op de universiteit.",
            "url": "https://maken.wikiwijs.nl/91192/Wiskundedidactiek_en_ICT",
            "description" : "Materiaal voor lerarenopleidingen en professionaliseringstrajecten gericht op wiskundedidactiek en ICT",
            "language" : "nl",
            "title_plain": "Wiskunde en Didactiek",
            "text_plain": "Leermateriaal over wiskunde en didactiek op de universiteit."
        }
        '''
        cls.elastic.index(index='test-nl', doc_type="_doc", body=material)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
        cls.elastic.indices.delete('test-nl')
        # FIXME: Ugly hack to kill open connections. Somehow it doesn't work on Github Actions otherwise.
        # There seems to be a running query for the filter tree which doesn't terminate in time.
        with connection.cursor() as c:
            c.execute("SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'test_edushare' AND pid <> pg_backend_pid();")

    def test_home_page(self):
        self.selenium.get(self.live_server_url)

        search = self.selenium.find_element_by_css_selector(".search.main__info_search input[type=search]")
        button = self.selenium.find_element_by_css_selector(".search.main__info_search button")

        search.send_keys("Wiskunde")
        button.click()

        self.selenium.find_element_by_xpath("//*[text()[contains(., 'Didactiek van wiskundig denken')]]")
