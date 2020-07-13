from django.conf import settings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from e2e_tests.base import ElasticSearchTestCase
from e2e_tests.elasticsearch_fixtures.elasticsearch import generate_nl_material


class TestSearch(ElasticSearchTestCase):
    fixtures = ['filter-categories', 'locales']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.material = generate_nl_material()
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX, body=cls.material
        )

    def test_search(self):
        self.selenium.get(self.live_server_url)

        search = self.selenium.find_element_by_css_selector(".search.main__info_search input[type=search]")
        button = self.selenium.find_element_by_css_selector(".search.main__info_search button")

        search.send_keys("Wiskunde")
        button.click()

        self.selenium.find_element_by_xpath("//*[text()[contains(., 'Didactiek van wiskundig denken')]]")

    def test_search_by_author(self):
        material_path = f"/materialen/{self.material.get('external_id')}"
        self.selenium.get(f"{self.live_server_url}{material_path}")

        author_link = self.selenium.find_element_by_css_selector(".material__info_author a")
        author_link.click()

        search_results = self.selenium.find_elements_by_css_selector(".materials__item_wrapper.tile__wrapper")
        self.assertEqual(len(search_results), 1)

    def test_search_by_publisher(self):
        material_path = f"/materialen/{self.material.get('external_id')}"
        self.selenium.get(f"{self.live_server_url}{material_path}")

        author_link = self.selenium.find_element_by_css_selector(".material__info_publishers a")
        author_link.click()

        search_results = self.selenium.find_elements_by_css_selector(".materials__item_wrapper.tile__wrapper")
        self.assertEqual(len(search_results), 1)


class TestSearchFiltering(ElasticSearchTestCase):
    fixtures = ['filter-categories', 'locales']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["HBO"], file_type="text", source="wikiwijsmaken")
        )
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["WO"], file_type="text", source="wikiwijsmaken")
        )
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["WO"], file_type="text", source="surf")
        )
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["WO"], file_type="video", source="surf")
        )
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["HBO"], file_type="video", source="surf")
        )

    def test_filter_search(self):
        self.selenium.get(self.live_server_url)
        self.selenium.find_element_by_css_selector(".search.main__info_search input[type=search]").send_keys("Wiskunde")
        self.selenium.find_element_by_css_selector(".search.main__info_search button").click()

        # Open filter categories
        educational_levels = self.selenium.find_element_by_xpath("//li[.//h4[text()[contains(., 'Onderwijsniveau')]]]")
        educational_levels.click()
        file_types = self.selenium.find_element_by_xpath("//li[.//h4[text()[contains(., 'Soort materiaal')]]]")
        file_types.click()
        source_category = self.selenium.find_element_by_xpath("//li[.//h4[text()[contains(., 'Bron')]]]")
        source_category.click()

        # Initial filter state
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#video ~ label"), "Video (2)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#text ~ label"), "Tekst (3)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#WO ~ label"), "WO (3)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#HBO ~ label"), "HBO (2)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#surf ~ label"), "SURF (3)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#wikiwijsmaken ~ label"), "Wikiwijs Maken (2)"))

        # Filter on WO
        educational_levels.find_element_by_css_selector("input").click()
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#video ~ label"), "Video (1)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#text ~ label"), "Tekst (2)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#WO ~ label"), "WO (3)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#HBO ~ label"), "HBO (2)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#surf ~ label"), "SURF (2)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#wikiwijsmaken ~ label"), "Wikiwijs Maken (1)"))

        # Filter on Tekst
        file_types.find_element_by_css_selector("input").click()
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#WO ~ label"), "WO (2)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#HBO ~ label"), "HBO (1)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#video ~ label"), "Video (1)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#text ~ label"), "Tekst (2)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#surf ~ label"), "SURF (1)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#wikiwijsmaken ~ label"), "Wikiwijs Maken (1)"))

        # Filter on SURF
        source_category.find_element_by_css_selector("input").click()
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#WO ~ label"), "WO (1)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#video ~ label"), "Video (1)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#text ~ label"), "Tekst (1)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#surf ~ label"), "SURF (1)"))
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#wikiwijsmaken ~ label"), "Wikiwijs Maken (1)"))
