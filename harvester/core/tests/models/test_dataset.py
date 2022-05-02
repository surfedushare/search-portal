from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from core.models import Collection
from core.tests.factories import DatasetFactory, DatasetVersionFactory, create_dataset_version


class TestDataset(TestCase):

    def setUp(self):
        super().setUp()
        now = make_aware(datetime.now())
        self.dataset = DatasetFactory()
        create_dataset_version(
            self.dataset, "0.0.1",
            created_at=now,
            include_current=True,
            copies=2,
            docs=22
        )

    def test_evaluate_dataset_version_pass(self):
        test_version = self.dataset.versions.filter(is_current=False).last()
        error_collections = self.dataset.evaluate_dataset_version(test_version)
        self.assertEqual(error_collections, [], "Expected identical versions to pass evaluation")
        test_version.document_set.last().delete()
        error_collections = self.dataset.evaluate_dataset_version(test_version)
        self.assertEqual(error_collections, [], "Expected versions with less than 5% difference to pass evaluation")
        self.dataset.versions.update(is_current=False)
        error_collections = self.dataset.evaluate_dataset_version(test_version)
        self.assertEqual(error_collections, [], "Expected no errors when no promoted previous versions exist")

    def test_evaluate_dataset_version_fail(self):
        error_collections = self.dataset.evaluate_dataset_version(DatasetVersionFactory.create(is_current=False))
        self.assertEqual(len(error_collections), 1, "Expected empty dataset version to generate error")
        self.assertIsInstance(error_collections[0], Collection)
        self.assertEqual(error_collections[0].name, "test")
        test_version = self.dataset.versions.filter(is_current=False).last()
        for doc in test_version.document_set.all()[:3]:
            doc.delete()
        error_collections = self.dataset.evaluate_dataset_version(test_version)
        self.assertEqual(len(error_collections), 1,"Expected dataset version with insufficient docs to generate error")
        self.assertIsInstance(error_collections[0], Collection)
        self.assertEqual(error_collections[0].name, "test")
