from e2e_tests.base import BaseTestCase

class TestBasicSearch(BaseTestCase):
    def test_home_page(self):
        self.selenium.get(self.live_server_url)

        self.selenium.find_element_by_css_selector(".search.main__info_search input[type=search]")
        self.selenium.find_element_by_css_selector(".search.main__info_search button")
