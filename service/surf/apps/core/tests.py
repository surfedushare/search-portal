from django.test import TestCase
from django.test import Client


class TestHomepage(TestCase):

    def test_health(self):
        c = Client()
        response = c.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['healthy'])
