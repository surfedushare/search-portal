from django.test import TestCase
from django.test import Client


class TestCore(TestCase):

    def test_health(self):
        c = Client()
        response = c.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['healthy'])

    def test_materials(self):
        c = Client()
        response = c.get("/api/v1/materials/")
        self.assertEqual(len(response.json()), 4)
        self.assertEqual(response.status_code, 200)
