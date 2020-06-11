from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from django.db import connection


class TestBasicSearch(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        cls.selenium = WebDriver(options=chrome_options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
        # FIXME: Ugly hack to kill open connections. Somehow it doesn't work on Github Actions otherwise.
        # There seems to be a running query for the filter tree which doesn't terminate in time.
        with connection.cursor() as c:
            c.execute("SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'test_edushare' AND pid <> pg_backend_pid();")

    def test_home_page(self):
        self.selenium.get(self.live_server_url)

        self.selenium.find_element_by_css_selector(".search.main__info_search input[type=search]")
        self.selenium.find_element_by_css_selector(".search.main__info_search button")
