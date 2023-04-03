from unittest.mock import patch
import json
from datetime import datetime
from bs4 import BeautifulSoup

from django.test import override_settings
from django.urls import reverse

from search_client.factories.learning_material import generate_nl_material
from e2e_tests.base import BaseOpenSearchTestCase
from e2e_tests.helpers import get_metadata_tree_mock


@patch("surf.apps.filters.metadata.requests.get", new=get_metadata_tree_mock)
@override_settings(OPENSEARCH_ALIAS_PREFIX="widget")
class TestWidget(BaseOpenSearchTestCase):

    alias_prefix = "widget"

    def assert_widget_response(self, response, expected_count):
        # Basic assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, "widget/index.html")
        # Assert that all links have the correct source parameter attached
        soup = BeautifulSoup(response.content, features="lxml")
        links = soup.select("a")
        for link in links:
            self.assertIn("source=widget", link["href"])
        # Results assertions
        self.assertEqual(response.context_data["record_count"], expected_count)
        required_fields = [
            "external_id",
            "has_parts",
            "published_at",
            "title",
            "avg_star_rating",
            "count_star_rating",
            "description",
            "lom_educational_levels",
            "technical_type",
            "authors"
        ]
        for record in response.context_data["records"]:
            for required_field in required_fields:
                self.assertIn(required_field, record)
            self.assertIsInstance(record["published_at"], (type(None), datetime,))
        # Translation assertions
        self.assertIsInstance(response.context_data["technical_type_translations"], dict)
        self.assertEqual(response.context_data["technical_type_translations"]["_field"], "Bestandstype")
        # Returns the records used while rendering the template for further assertions
        return response.context_data["records"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        math_and_education_studies = [
            "7afbb7a6-c29b-425c-9c59-6f79c845f5f0",  # math
            "0861c43d-1874-4788-b522-df8be575677f"  # onderwijskunde
        ]
        biology_studies = [
            "2b363227-8633-4652-ad57-c61f1efc02c8"
        ]
        biology_and_education_studies = biology_studies + [
            "0861c43d-1874-4788-b522-df8be575677f"
        ]

        cls.base_url = reverse("portal-widget")
        cls.search.index(
            index=cls.get_alias("nl"),
            body=generate_nl_material(educational_levels=["HBO"], source="surfsharekit",
                                      studies=math_and_education_studies),
        )
        cls.search.index(
            id="abc",
            index=cls.get_alias("nl"),
            body=generate_nl_material(educational_levels=["HBO"], source="surfsharekit",
                                      studies=math_and_education_studies, external_id="abc",
                                      title="De wiskunde van Pythagoras", description="Groots zijn zijn getallen")
        )
        cls.search.index(
            index=cls.get_alias("nl"),
            body=generate_nl_material(educational_levels=["HBO"], source="surfsharekit",
                                      copyright="cc-by-40", topic="biology", publisher_date="2018-04-16T22:35:09+02:00",
                                      studies=biology_and_education_studies),
        )
        cls.search.index(
            index=cls.get_alias("nl"),
            body=generate_nl_material(educational_levels=["HBO"], source="surfsharekit",
                                      topic="biology", publisher_date="2019-04-16T22:35:09+02:00",
                                      studies=biology_and_education_studies),
        )
        cls.search.index(
            index=cls.get_alias("nl"),
            body=generate_nl_material(educational_levels=["HBO"], technical_type="video", source="surfsharekit",
                                      topic="biology", studies=biology_studies),
            refresh=True  # always put refresh on the last material
        )

    def test_biology(self):
        response = self.client.get(f'{self.base_url}?search_text="biologie"')
        self.assert_widget_response(response, expected_count=3)

    def test_math(self):
        response = self.client.get(f'{self.base_url}?search_text="wiskunde"')
        self.assert_widget_response(response, expected_count=2)

    def test_studies_filter(self):
        expected_study = "0861c43d-1874-4788-b522-df8be575677f"
        filters = json.dumps({
            "studies": [expected_study]
        })
        response = self.client.get(f'{self.base_url}?search_text="wiskunde"&filters={filters}')
        records = self.assert_widget_response(response, expected_count=2)
        for record in records:
            study_ids = [study["id"] for study in record["studies"]]
            self.assertIn(expected_study, study_ids)

    def test_no_results(self):
        response = self.client.get(f'{self.base_url}?search_text="piskunde"')
        self.assert_widget_response(response, expected_count=0)

    def test_invalid_parameters(self):
        response = self.client.get(self.base_url)
        self.assertContains(response, "search_text", count=1, status_code=400)
        self.assertContains(response, "required", count=1, status_code=400)
        filters = json.dumps({
            "studies": "0861c43d-1874-4788-b522-df8be575677f"  # value should be a list
        })
        response = self.client.get(f'{self.base_url}?search_text="biologie"&filters={filters}')
        self.assertContains(response, "filters", count=1, status_code=400)
        self.assertContains(response, "not_a_list", count=1, status_code=400)
