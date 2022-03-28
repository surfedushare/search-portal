from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware
from django.contrib.auth.models import User

from core.tests.factories import DatasetFactory, create_dataset_version


class TestDatasetDocumentsAPI(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="supersurf")

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        created_time = make_aware(datetime.now())
        self.active_dataset = DatasetFactory.create(name="active test", is_active=True, is_latest=True)
        create_dataset_version(self.active_dataset, "0.0.1", created_time, include_current=True)
        self.inactive_dataset = DatasetFactory.create(name="inactive test", is_active=False, is_latest=False)
        create_dataset_version(self.inactive_dataset, "0.0.1", created_time, docs=1, include_current=False)

    def test_documents(self):
        response = self.client.get(f"/api/v1/dataset/{self.active_dataset.id}/documents/?page_size=2")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 5)
        self.assertIsNotNone(data["next"])
        self.assertIsNone(data["previous"])
        expected_keys = ["created_at", "id", "identity", "modified_at", "properties", "reference", "source"]
        for doc in data["results"]:
            self.assertEqual(sorted(list(doc.keys())), expected_keys)

    def test_metadata_documents(self):
        response = self.client.get("/api/v1/dataset/metadata-documents/?page_size=2")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 5)
        self.assertIsNotNone(data["next"])
        self.assertIsNone(data["previous"])
        expected_keys = ["created_at", "id", "language", "modified_at", "reference"]
        for doc in data["results"]:
            self.assertEqual(sorted(list(doc.keys())), expected_keys)
            for key in expected_keys:
                self.assertIsNotNone(doc[key])
