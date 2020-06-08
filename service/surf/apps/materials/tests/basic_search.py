from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from chromedriver_py import binary_path


class TestBasicSearch(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        cls.selenium = WebDriver(options=chrome_options, executable_path=binary_path)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_home_page(self):
        self.selenium.get(self.live_server_url)
        print(self.live_server_url)
        self.selenium.find_element_by_css_selector(".search.main__info_search input[type=search]")
        self.selenium.find_element_by_css_selector(".search.main__info_search button")
