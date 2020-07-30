import os
import factory
from e2e_tests.base import BaseTestCase
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from e2e_tests.factories import UserFactory, CommunityFactory, TeamFactory, CommunityDetailFactory
from e2e_tests.helpers import login, replace_content
from surf.statusenums import PublishStatus


class TestCommunities(BaseTestCase):
    def setUp(cls):
        super().setUp()
        cls.user = UserFactory.create()
        login(cls, cls.user)

    def test_community_overview(self):
        CommunityFactory.create(
            name="public",
            dutch_details=factory.RelatedFactory(
                CommunityDetailFactory,
                factory_related_name="community",
                dutch=True,
                title="Publieke community"
            )
        )
        CommunityFactory.create(
            name="draft",
            publish_status=PublishStatus.DRAFT,
            dutch_details=factory.RelatedFactory(
                CommunityDetailFactory,
                factory_related_name="community",
                dutch=True,
                title="Niet-gepubliceerde community"
            )
        )
        my_draft_community = CommunityFactory.create(
            name="my-draft",
            publish_status=PublishStatus.DRAFT,
            dutch_details=factory.RelatedFactory(
                CommunityDetailFactory,
                factory_related_name="community",
                dutch=True,
                title="Mijn draft community"
            )
        )
        TeamFactory.create(user=self.user, community=my_draft_community)
        my_published_community = CommunityFactory.create(
            name="my-published",
            dutch_details=factory.RelatedFactory(
                CommunityDetailFactory,
                factory_related_name="community",
                dutch=True,
                title="Mijn community"
            )
        )
        TeamFactory.create(user=self.user, community=my_published_community)

        self.selenium.get(f"{self.live_server_url}/communities")
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".communities__items"), "Publieke community"
            )
        )
        communities = self.selenium.find_element_by_css_selector(".communities__items")
        self.assertTrue("Niet-gepubliceerde community" not in communities.text)

        self.selenium.find_element_by_css_selector(".my-communities-tab").click()

        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".communities__items.my-communities"), "Mijn community"
            )
        )

        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".communities__items.my-communities"), "Mijn draft community"
            )
        )

        self.selenium.find_element_by_css_selector(".draft-switch label").click()

        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".communities__items.my-communities"), "Mijn community"
            )
        )

        my_communities = self.selenium.find_element_by_css_selector(".communities__items.my-communities")
        self.assertTrue("Mijn draft community" not in my_communities.text)

    def test_community_overview_without_own_communities(self):
        CommunityFactory.create()
        self.selenium.get(f"{self.live_server_url}/communities")
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".communities__items"), "Ethiek"
            )
        )
        self.assertTrue(len(self.selenium.find_elements_by_css_selector(".my-communities-tab")) == 0)

    def test_community_overview_language_switch(self):
        community = CommunityFactory.create()
        TeamFactory.create(user=self.user, community=community)
        self.selenium.get(f"{self.live_server_url}/communities")
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".communities__item"),
                "Ethiek"
            )
        )

        # Switch to English
        self.selenium.find_element_by_css_selector("a.lang").click()

        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".communities__item"),
                "Ethics"
            )
        )

    def test_community_editing(self):
        community = CommunityFactory.create()
        TeamFactory.create(user=self.user, community=community)
        self.selenium.get(f"{self.live_server_url}/mijn/community/{community.id}")
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
        self.selenium.find_element_by_css_selector(".crop-popup button.crop").click()

        en_logo = self.selenium.find_element_by_css_selector("#logo_en input")
        en_logo.send_keys(os.path.dirname(__file__)+"/images/community_logo.png")
        self.selenium.find_element_by_css_selector("#logo_en .crop-popup button.crop").click()

        nl_featured = self.selenium.find_element_by_css_selector("#featured_image_nl input")
        nl_featured.send_keys(os.path.dirname(__file__)+"/images/community_featured_image.png")
        self.selenium.find_element_by_css_selector("#featured_image_nl .crop-popup button.crop").click()

        en_featured = self.selenium.find_element_by_css_selector("#featured_image_en input")
        en_featured.send_keys(os.path.dirname(__file__)+"/images/community_featured_image.png")
        self.selenium.find_element_by_css_selector("#featured_image_en .crop-popup button.crop").click()

        crop_popup = self.selenium.find_element_by_css_selector("#featured_image_en .crop-popup")
        WebDriverWait(self.selenium, 2).until(
            EC.staleness_of(crop_popup)
        )

        self.selenium.find_element_by_css_selector(".communities__form__buttons button[type='submit']").click()
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "body"), "Gegevens opgeslagen!")
        )

        # Dutch preview
        self.selenium.find_element_by_css_selector(".communities__form__buttons button.preview").click()
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".preview-block"), "Nieuwe titel")
        )
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".preview-block"), "Nieuwe beschrijving")
        )

        website = self.selenium.find_element_by_css_selector(".how_work_link").get_attribute("href")
        self.assertEqual(website, "https://www.surf.nl/")

        featured_image = self.selenium.find_element_by_css_selector(".preview__bg_block-img").get_attribute("src")
        self.assertIn("data:image/png", featured_image)

        # English preview
        self.selenium.find_element_by_css_selector("a.lang").click()

        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".preview-block"), "New title")
        )
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".preview-block"), "New description")
        )

        website = self.selenium.find_element_by_css_selector(".how_work_link").get_attribute("href")
        self.assertEqual(website, "https://www.surf.com/")

        featured_image = self.selenium.find_element_by_css_selector(".preview__bg_block-img").get_attribute("src")
        self.assertIn("data:image/png", featured_image)


class TestCommunityTabVisibility(BaseTestCase):
    def test_community_not_authenticated(self):
        self.community = CommunityFactory.create()
        self.selenium.get(f"{self.live_server_url}/communities")
        WebDriverWait(self.selenium, 2).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, ".communities__items"), "Ethiek"
            )
        )
        self.assertTrue(len(self.selenium.find_elements_by_css_selector(".my-communities-tab")) == 0)
