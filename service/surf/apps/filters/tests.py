from django.test import TestCase
from django.test import Client


class TestFilters(TestCase):

    fixtures = ['filter-categories', 'locales']

    def test_filter_categories(self):
        client = Client()
        response = client.get("/api/v1/filter-categories/")
        count = response.json()['count']
        results = response.json()['results']
        names = [result['name'] for result in results]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count, 9)
        self.assertEqual(names, ['Bron', 'Bruikbaar als', 'Gebruiksrechten', 'Onderwijsniveau', 'Publicatiedatum', 'Soort materiaal', 'Taal', 'Thema', 'Vakgebied'])
