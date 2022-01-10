from unittest.mock import patch

from django.conf import settings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from e2e_tests.base import BaseLiveServerTestCase
from e2e_tests.factories import UserFactory, CommunityFactory, TeamFactory, CollectionFactory, MaterialFactory
from e2e_tests.helpers import login, get_metadata_tree_mock
from e2e_tests.elasticsearch_fixtures.elasticsearch import generate_nl_material


@patch("surf.apps.filters.metadata.requests.get", new=get_metadata_tree_mock)
class TestCollectionMaterials(BaseLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.material = generate_nl_material()
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX, body=cls.material
        )

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.community = CommunityFactory.create()
        TeamFactory.create(user=self.user, community=self.community)
        self.collection = CollectionFactory.create(communities=[self.community])
        login(self, self.user)

    def test_add_material(self):
        self.selenium.get(f"{self.live_server_url}/mijn/collectie/{self.collection.id}")
        self.selenium.find_element_by_css_selector(".materials__add__link").click()
        search = self.selenium.find_element_by_css_selector(".search-container input[type=search]")
        search.send_keys("Wiskunde")
        self.selenium.find_element_by_css_selector(".search-container button[type='submit']").click()
        self.selenium.find_element_by_xpath("//*[text()[contains(., 'Didactiek van wiskundig denken')]]")
        self.selenium.find_element_by_css_selector(".search__materials .select-icon").click()
        self.selenium.find_element_by_xpath("//button[text()[contains(., '1 toevoegen')]]").click()
        self.selenium.find_element_by_xpath("//*[text()[contains(., 'Didactiek van wiskundig denken')]]")
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".collection__materials"), "Didactiek van wiskundig denken"
            )
        )

    def test_remove_material(self):
        MaterialFactory.create(collections=[self.collection], external_id=self.material["external_id"])
        self.selenium.get(f"{self.live_server_url}/mijn/collectie/{self.collection.id}")
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".collection__materials"), "Didactiek van wiskundig denken"
            )
        )
        self.selenium.find_element_by_css_selector(".collection__materials .select-icon").click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".collection__materials"), "Niet gevonden"
            )
        )
