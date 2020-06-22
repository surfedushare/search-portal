from django.test import TestCase
from django.test import Client


class TestFilters(TestCase):

    fixtures = ['filter-categories', 'locales']

    def test_filter_categories(self):
        self.skipTest("Enable this when elastic search on github actions works")
        client = Client()
        response = client.get("/api/v1/filter-categories/")
        number_of_categories = response.json()['count']
        results = response.json()['results']
        names = [result['name'] for result in results]

        parent_in_filter_category = "parent" in results[0]
        external_id_in_filter_category = "external_id" in results[0]
        enabled_by_default_in_filter_category = "enabled_by_default" in results[0]
        item_count_in_filter_category = "enabled_by_default" in results[0]
        children_in_filter_category = "children" in results[0]
        is_hidden_in_filter_category = "is_hidden" in results[0]
        title_translations_in_filter_category = "title_translations" in results[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(number_of_categories, 9)
        self.assertEqual(names, ['Bron', 'Bruikbaar als', 'Gebruiksrechten', 'Onderwijsniveau',
                                 'Publicatiedatum', 'Soort materiaal', 'Taal', 'Thema', 'Vakgebied'])

        self.assertTrue(parent_in_filter_category, msg=None)
        self.assertTrue(external_id_in_filter_category, msg=None)
        self.assertTrue(enabled_by_default_in_filter_category, msg=None)
        self.assertTrue(item_count_in_filter_category, msg=None)
        self.assertTrue(children_in_filter_category, msg=None)
        self.assertTrue(is_hidden_in_filter_category, msg=None)
        self.assertTrue(title_translations_in_filter_category, msg=None)
