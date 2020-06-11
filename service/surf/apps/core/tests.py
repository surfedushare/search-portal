from django.test import SimpleTestCase
from django.test import Client


class TestCore(SimpleTestCase):

    def test_health(self):
        client = Client()
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['healthy'])
