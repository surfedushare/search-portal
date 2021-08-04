from django.test import TestCase
from django.test import Client


class TestLocales(TestCase):

    fixtures = ['locales', 'privacy_statements']

    def test_locales_en(self):
        client = Client()
        response = client.get("/locales/en")
        results = response.json()
        selections = results["My-selections"]
        logout = results["logout"]
        html = results["html-Footer-info-text"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(selections, "My selections")
        self.assertEqual(logout, "Log out")
        self.assertTrue(html.startswith("<p>edusources is offered by SURF,"))

    def test_locales_nl(self):
        client = Client()
        response = client.get("/locales/nl")
        results = response.json()
        selections = results["My-selections"]
        logout = results["logout"]
        html = results["html-Footer-info-text"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(selections, "Mijn selecties")
        self.assertEqual(logout, "Uitloggen")
        self.assertTrue(html.startswith("<p>edusources wordt aangeboden door SURF,"))
