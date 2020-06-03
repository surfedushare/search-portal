from django.test import TestCase
from django.test import Client


class TestFilters(TestCase):

    fixtures = ['filter-categories', 'locales']

    def test_filter_categories(self):
        client = Client()
        response = client.get("/api/v1/filter-categories/")
        self.assertEqual(response.status_code, 200)
