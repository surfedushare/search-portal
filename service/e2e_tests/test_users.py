from django.test import override_settings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from e2e_tests.base import BaseLiveServerTestCase
from e2e_tests.factories import UserFactory, DataGoalPermissionFactory
from e2e_tests.helpers import login


class TestUsers(BaseLiveServerTestCase):

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.data_goal_permission = DataGoalPermissionFactory.create(user=self.user)
        login(self, self.user)

    @override_settings(DEBUG=True)
    def test_delete_user(self):
        self.selenium.get(f"{self.live_server_url}/mijn/privacy")
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".info .title"), "Mijn privacy"
            ),
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".privacy__form__label"), "Communities"
            ),
        )
        self.selenium.find_element_by_css_selector(".privacy input").is_selected()
        self.selenium.find_element_by_css_selector(".permission-container .switch-input").click()

        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".privacy__form__button"), "Verwijder account en log uit"
            )
        )

        self.selenium.find_element_by_css_selector(".privacy__form__button").click()

        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".popup__title"), "Account verwijderen"
            )
        )
        self.selenium.find_element_by_css_selector(".popup-content__actions button").click()

        WebDriverWait(self.selenium, 10).until(
            EC.url_to_be("https://engine.surfconext.nl/logout")
        )
