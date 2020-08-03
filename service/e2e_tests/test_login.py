from e2e_tests.base import BaseTestCase
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class TestLogin(BaseTestCase):
    def test_expired_session_token(self):
        self.selenium.get(self.live_server_url)
        self.selenium.execute_script(
            "window.localStorage.setItem(arguments[0], arguments[1]);",
            "surf_token",
            "fake-session"
        )
        self.selenium.get(self.live_server_url)
        WebDriverWait(self.selenium, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".main_block"))
        )
