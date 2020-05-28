from django.test import TestCase
from django.test import Client


class TestFilters(TestCase):

    fixtures = ['filter-categories', 'locales']

    def test_filter_categories(self):
        c = Client()
        response = c.get("/api/v1/filter-categories/")
        print(response.json()['results'][0])
        self.assertEqual(response.status_code, 200)
