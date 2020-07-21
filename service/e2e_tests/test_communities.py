import os
from e2e_tests.base import BaseTestCase
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from e2e_tests.factories import UserFactory, CommunityFactory, TeamFactory
from e2e_tests.helpers import login, replace_content


class TestCommunities(BaseTestCase):
    fixtures = ['filter-categories', 'complete_locales']

    def setUp(cls):
        cls.user = UserFactory.create()
        cls.community = CommunityFactory.create()
        TeamFactory.create(user=cls.user, community=cls.community)
        login(cls, cls.user)

    def test_community_overview_language_switch(self):
        self.selenium.get(f"{self.live_server_url}/mijn/communities")
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".communities__item_wrapper"),
                "Ethiek"
            )
        )

        # Switch to English
        self.selenium.find_element_by_css_selector("a.lang").click()

        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".communities__item_wrapper"),
                "Ethics"
            )
        )

    def test_community_editing(self):
        self.selenium.get(f"{self.live_server_url}/mijn/community/{self.community.id}")
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "body"),
                "Mijn Community"
            )
        )
        replace_content(self.selenium.find_element_by_id("title_nl"), 'Nieuwe titel')
        replace_content(self.selenium.find_element_by_id("title_en"), 'New title')
        replace_content(
            self.selenium.find_element_by_css_selector("#description_nl .ProseMirror"),
            'Nieuwe beschrijving'
        )
        replace_content(
            self.selenium.find_element_by_css_selector("#description_en .ProseMirror"),
            'New description'
        )
        replace_content(self.selenium.find_element_by_id("website_nl"), 'https://www.surf.nl')
        replace_content(self.selenium.find_element_by_id("website_en"), 'https://www.surf.com')

        nl_logo = self.selenium.find_element_by_css_selector("#logo_nl input")
        nl_logo.send_keys(os.path.dirname(__file__)+"/images/community_logo.png")

        en_logo = self.selenium.find_element_by_css_selector("#logo_en input")
        en_logo.send_keys(os.path.dirname(__file__)+"/images/community_logo.png")

        nl_featured = self.selenium.find_element_by_css_selector("#featured_image_nl input")
        nl_featured.send_keys(os.path.dirname(__file__)+"/images/community_featured_image.png")

        en_featured = self.selenium.find_element_by_css_selector("#featured_image_en input")
        en_featured.send_keys(os.path.dirname(__file__)+"/images/community_featured_image.png")

        self.selenium.find_element_by_css_selector(".communities__form__buttons button[type='submit']").click()
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "body"), "Gegevens opgeslagen!")
        )

        # Dutch preview
        self.selenium.find_element_by_css_selector(".communities__form__buttons a").click()
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "section.community"), "Nieuwe titel")
        )
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "section.community"), "Nieuwe beschrijving")
        )

        website = self.selenium.find_element_by_css_selector(".how_work_link").get_attribute("href")
        self.assertEqual(website, "https://www.surf.nl/")

        featured_image = self.selenium.find_element_by_css_selector(".preview__bg_block-img").get_attribute("src")
        self.assertIn("community_featured_image", featured_image)

        # English preview
        self.selenium.find_element_by_css_selector("a.lang").click()

        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "section.community"), "New title")
        )
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "section.community"), "New description")
        )

        website = self.selenium.find_element_by_css_selector(".how_work_link").get_attribute("href")
        self.assertEqual(website, "https://www.surf.com/")

        featured_image = self.selenium.find_element_by_css_selector(".preview__bg_block-img").get_attribute("src")
        self.assertIn("community_featured_image", featured_image)
