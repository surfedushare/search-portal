from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from e2e_tests.base import BaseTestCase
from e2e_tests.factories import UserFactory, CommunityFactory, TeamFactory, CollectionFactory
from e2e_tests.helpers import login, replace_content


class TestCollections(BaseTestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.community = CommunityFactory.create()
        TeamFactory.create(user=self.user, community=self.community)
        login(self, self.user)

    def test_add_collection(self):
        self.selenium.get(f"{self.live_server_url}/mijn/community/{self.community.id}")
        self.selenium.find_element_by_css_selector(".collections-tab").click()
        self.selenium.find_element_by_css_selector(".collections__add__link").click()
        replace_content(self.selenium.find_element_by_id("collection_title_nl"), 'Mijn collectie')
        replace_content(self.selenium.find_element_by_id("collection_title_en"), 'My collection')
        self.selenium.find_element_by_css_selector(".add-collection button[type='submit']").click()
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".add-collection"), "Je collectie is aangemaakt")
        )

    def test_remove_collection(self):
        CollectionFactory.create(communities=[self.community])
        self.selenium.get(f"{self.live_server_url}/mijn/community/{self.community.id}")
        self.selenium.find_element_by_css_selector(".collections-tab").click()
        self.selenium.find_element_by_css_selector(".collections__item .select-icon").click()
        self.selenium.find_element_by_css_selector(".communities__form__buttons button[type='submit']").click()
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "body"), "Gegevens opgeslagen!")
        )
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".collections"), "Geen collecties")
        )
