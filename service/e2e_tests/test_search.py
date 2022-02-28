from unittest.mock import patch

from django.conf import settings
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from e2e_tests.base import BaseLiveServerTestCase
from e2e_tests.elasticsearch_fixtures.elasticsearch import generate_nl_material
from e2e_tests.helpers import get_metadata_tree_mock


@patch("surf.apps.filters.metadata.requests.get", new=get_metadata_tree_mock)
class TestSearch(BaseLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.material = generate_nl_material()
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX, body=cls.material
        )

    def test_search(self):
        self.selenium.get(self.live_server_url)

        search = self.selenium.find_element_by_css_selector(".search input[type=search]")
        button = self.selenium.find_element_by_css_selector(".search button")

        search.send_keys("Wiskunde")
        button.click()

        WebDriverWait(self.selenium, self.explicit_wait).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section.spinner")))

        self.selenium.find_element_by_xpath("//*[text()[contains(., 'Didactiek van wiskundig denken')]]")

    def test_search_by_author_from_searchbox(self):
        self.selenium.get(self.live_server_url)

        search = self.selenium.find_element_by_css_selector(".search input[type=search]")
        button = self.selenium.find_element_by_css_selector(".search button")

        search.send_keys("Theo")
        button.click()

        WebDriverWait(self.selenium, self.explicit_wait).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section.spinner")))

        search_results = self.selenium.find_elements_by_css_selector(".materials__item_wrapper.tile__wrapper")
        self.assertEqual(len(search_results), 1)
        self.selenium.find_element_by_xpath("//*[text()[contains(., 'Didactiek van wiskundig denken')]]")

    def test_search_by_author(self):
        material_path = f"/materialen/{self.material.get('external_id')}"
        self.selenium.get(f"{self.live_server_url}{material_path}")

        author_link = self.selenium.find_element_by_css_selector(".material__info_author a")
        author_link.click()

        WebDriverWait(self.selenium, self.explicit_wait).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section.spinner")))

        search_results = self.selenium.find_elements_by_css_selector(".materials__item_wrapper.tile__wrapper")
        self.assertEqual(len(search_results), 1)

    def test_search_by_publisher(self):
        material_path = f"/materialen/{self.material.get('external_id')}"
        self.selenium.get(f"{self.live_server_url}{material_path}")

        author_link = self.selenium.find_element_by_css_selector(".material__info_publishers a")
        author_link.click()

        WebDriverWait(self.selenium, self.explicit_wait).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section.spinner")))

        search_results = self.selenium.find_elements_by_css_selector(".materials__item_wrapper.tile__wrapper")
        self.assertEqual(len(search_results), 1)

    def test_search_did_you_mean(self):

        self.selenium.get(self.live_server_url)

        search = self.selenium.find_element_by_css_selector(".search input[type=search]")
        button = self.selenium.find_element_by_css_selector(".search button")

        search.send_keys("didaktiek")
        button.click()

        WebDriverWait(self.selenium, self.explicit_wait).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section.spinner")))

        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".not_found"), "Geen resultaten voor"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".not_found"), "didaktiek"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".not_found"), "Bedoelde je"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".not_found"), "didactiek"))

        spelling_link = self.selenium.find_element_by_css_selector(".not_found a")
        spelling_link.click()

        WebDriverWait(self.selenium, self.explicit_wait).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section.spinner")))

        self.selenium.find_element_by_xpath("//*[text()[contains(., 'Didactiek van wiskundig denken')]]")

    def test_search_no_results(self):

        self.selenium.get(self.live_server_url)

        search = self.selenium.find_element_by_css_selector(".search input[type=search]")
        button = self.selenium.find_element_by_css_selector(".search button")

        search.send_keys("kauwgomballenautomaat")
        button.click()

        WebDriverWait(self.selenium, self.explicit_wait).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section.spinner")))

        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".not_found"), "Niet gevonden"))


@patch("surf.apps.filters.metadata.requests.get", new=get_metadata_tree_mock)
class TestSearchFiltering(BaseLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["HBO"], source="wikiwijsmaken")
        )
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["WO"], source="wikiwijsmaken")
        )
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["WO"], source="edusources")
        )
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["WO"], technical_type="video", source="edusources")
        )
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["HBO"], technical_type="video", source="edusources")
        )

    def test_filter_search(self):
        action = ActionChains(self.selenium)
        self.selenium.get(self.live_server_url)
        self.selenium.find_element_by_css_selector(".search input[type=search]").send_keys("Wiskunde")
        self.selenium.find_element_by_css_selector(".search button").click()

        # Open filter categories
        educational_levels = self.selenium.find_element_by_xpath("//li[.//h4[text()[contains(., 'Onderwijsniveau')]]]")
        educational_levels.click()
        technical_types = self.selenium.find_element_by_xpath("//li[.//h4[text()[contains(., 'Bestandstype')]]]")
        technical_types.click()
        source_category = self.selenium.find_element_by_xpath("//li[.//h4[text()[contains(., 'Bron')]]]")
        source_category.click()

        # Initial filter state
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#video ~ label"), "Video (2)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#document ~ label"), "Document (3)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#WO ~ label"), "WO (3)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#HBO ~ label"), "HBO (2)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#sharekit ~ label"), "Sharekit (3)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#wikiwijsmaken ~ label"), "Wikiwijs Maken (2)"))

        # Filter on WO
        educational_levels.find_element_by_css_selector("input").click()
        WebDriverWait(self.selenium, self.explicit_wait).until(EC.visibility_of(educational_levels))
        action.move_to_element(source_category).perform()
        WebDriverWait(self.selenium, self.explicit_wait).until(EC.visibility_of(technical_types))
        technical_types.click()
        WebDriverWait(self.selenium, self.explicit_wait).until(EC.visibility_of(source_category))
        source_category.click()

        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#video ~ label"), "Video (1)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#document ~ label"), "Document (2)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#WO ~ label"), "WO (3)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#HBO ~ label"), "HBO (2)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#sharekit ~ label"), "Sharekit (2)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#wikiwijsmaken ~ label"), "Wikiwijs Maken (1)"))

        # TODO: below here tests will sometimes fail on Github.
        # Which means that for instance the "push" suite succeeds while the "pull_request" suite does not.
        # Locally the test passes.
        # The tests fail with a TimeoutException without a message so it's not entirely clear what goes wrong here.
        # We should re-enable this test.
        # self.skipTest("Skipped due to strange Github behaviour")
        # Filter on Document
        technical_types.find_element_by_css_selector("input").click()
        WebDriverWait(self.selenium, self.explicit_wait).until(EC.visibility_of(technical_types))
        action.move_to_element(source_category).perform()
        WebDriverWait(self.selenium, self.explicit_wait).until(EC.visibility_of(source_category))
        source_category.click()

        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#WO ~ label"), "WO (2)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#HBO ~ label"), "HBO (1)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#video ~ label"), "Video (1)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#document ~ label"), "Document (2)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#sharekit ~ label"), "Sharekit (1)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#wikiwijsmaken ~ label"), "Wikiwijs Maken (1)"))

        # Filter on Sharekit
        source_category.find_element_by_css_selector("input").click()
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#WO ~ label"), "WO (1)"))
        # WebDriverWait(self.selenium, self.explicit_wait).until(
        #     EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#video ~ label"), "Video (2)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#document ~ label"), "Document (1)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#sharekit ~ label"), "Sharekit (1)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#wikiwijsmaken ~ label"), "Wikiwijs Maken (1)"))

    def test_filter_search_home_by_education_level(self):
        """
        Loading the homepage, selecting WO as educational level and making a search
        """
        self.selenium.get(self.live_server_url)
        select_element = self.selenium.find_element_by_css_selector(".search select")
        select = Select(select_element)
        select.select_by_value("WO")
        self.selenium.find_element_by_css_selector(".search input[type=search]").send_keys("Wiskunde")
        self.selenium.find_element_by_css_selector(".search button").click()
        # Checking search results and educational level filters should be visible and selected
        self.selenium.find_element_by_xpath("//*[text()[contains(., 'Didactiek van wiskundig denken')]]")
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//li[.//h4[text()[contains(., 'Onderwijsniveau')]]]"),
                "Onderwijsniveau"
            )
        )
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.element_located_selection_state_to_be((By.CSS_SELECTOR, "#WO"), True))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.element_located_selection_state_to_be((By.CSS_SELECTOR, "#HBO"), False))

        # Now we'll be clicking open a lot of the other filters to make sure their counts are correct
        technical_types = self.selenium.find_element_by_xpath("//li[.//h4[text()[contains(., 'Bestandstype')]]]")
        technical_types.click()
        source_category = self.selenium.find_element_by_xpath("//li[.//h4[text()[contains(., 'Bron')]]]")
        source_category.click()
        # And check the actual counts per filter
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#video ~ label"), "Video (1)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#document ~ label"), "Document (2)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#sharekit ~ label"), "Sharekit (2)"))
        WebDriverWait(self.selenium, self.explicit_wait).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#wikiwijsmaken ~ label"), "Wikiwijs Maken (1)"))
