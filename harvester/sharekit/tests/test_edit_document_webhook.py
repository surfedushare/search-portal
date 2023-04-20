import json

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.timezone import now

from core.models import Document
from sharekit.tests.factories import SharekitMetadataHarvestFactory


TEST_HARVESTER_WEBHOOK_SECRET = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"


@override_settings(HARVESTER_WEBHOOK_SECRET=TEST_HARVESTER_WEBHOOK_SECRET)
class TestEditDocumentWebhook(TestCase):

    fixtures = ["datasets-history"]

    @classmethod
    def load_sharekit_test_data(cls):
        delta_response = SharekitMetadataHarvestFactory.create(is_initial=False, number=0)
        content_type, delta = delta_response.content
        delta_records = delta["data"]
        return {
            "create": delta_records[2],
            "update": delta_records[0],
            "delete": delta_records[1]
        }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_start_time = now()
        cls.webhook_secret = TEST_HARVESTER_WEBHOOK_SECRET
        cls.webhook_url = reverse("edit-document-webhook", args=("edusources", cls.webhook_secret,))
        cls.test_ip = "20.56.15.206"
        cls.test_data = cls.load_sharekit_test_data()

    def call_webhook(self, url, ip=None, verb="create"):
        return self.client.post(
            url,
            data=self.test_data[verb],
            content_type="application/vnd.api+json",
            HTTP_X_FORWARDED_FOR=ip or self.test_ip
        )

    def test_invalid_secret(self):
        no_uuid_secret_url = self.webhook_url.replace(self.webhook_secret, "invalid")
        no_uuid_response = self.call_webhook(no_uuid_secret_url)
        self.assertEqual(no_uuid_response.status_code, 404)
        invalid_secret = self.webhook_secret.replace(self.webhook_secret[:8], "b" * 8)
        invalid_secret_url = self.webhook_url.replace(self.webhook_secret, invalid_secret)
        invalid_secret_response = self.call_webhook(invalid_secret_url)
        self.assertEqual(invalid_secret_response.status_code, 403)
        self.assertEqual(invalid_secret_response.reason_phrase, "Webhook not allowed in this environment")

    def test_invalid_ip(self):
        invalid_ip_response = self.call_webhook(self.webhook_url, ip="127.6.6.6")
        self.assertEqual(invalid_ip_response.status_code, 403)
        self.assertEqual(invalid_ip_response.reason_phrase, "Webhook not allowed from source")

    def test_invalid_data(self):
        encoded_data = json.dumps(self.test_data["create"])
        invalid_data_response = self.client.post(
            self.webhook_url,
            data=encoded_data[:10],  # an arbitrarily chosen mutilation of the JSON
            content_type="text/html",
            HTTP_X_FORWARDED_FOR=self.test_ip
        )
        self.assertEqual(invalid_data_response.status_code, 400)
        self.assertEqual(invalid_data_response.reason_phrase, "Invalid JSON")

    def test_create(self):
        self.assertIsNone(
            Document.objects.filter(reference="3e45b9e3-ba76-4200-a927-2902177f1f6c").last(),
            "Document with external_id 3e45b9e3-ba76-4200-a927-2902177f1f6c should not exist before the test"
        )
        create_response = self.call_webhook(self.webhook_url)
        self.assertEqual(create_response.status_code, 200)
        create_document = Document.objects.filter(reference="3e45b9e3-ba76-4200-a927-2902177f1f6c").last()
        self.assertIsNotNone(create_document)
        self.assertGreater(create_document.created_at, self.test_start_time)
        self.assertGreater(create_document.modified_at, self.test_start_time)

    def test_update(self):
        update_response = self.call_webhook(self.webhook_url, verb="update")
        self.assertEqual(update_response.status_code, 200)
        update_document = Document.objects.filter(reference="5be6dfeb-b9ad-41a8-b4f5-94b9438e4257").last()
        self.assertIsNotNone(update_document)
        self.assertLess(update_document.created_at, self.test_start_time)
        self.assertGreater(update_document.modified_at, self.test_start_time)
        self.assertEqual(update_document.properties["title"], "Using a Vortex (responsibly) | Wageningen UR")

    def test_delete(self):
        delete_response = self.call_webhook(self.webhook_url, verb="delete")
        self.assertEqual(delete_response.status_code, 200)
        delete_document = Document.objects.filter(reference="63903863-6c93-4bda-b850-277f3c9ec00e").last()
        self.assertIsNotNone(delete_document)
        self.assertLess(delete_document.created_at, self.test_start_time)
        self.assertGreater(delete_document.modified_at, self.test_start_time)
        self.assertEqual(delete_document.properties["state"], "deleted")
