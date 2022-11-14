from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from core.models import Collection
from core.tests.factories import DatasetFactory, DatasetVersionFactory, create_dataset_version, DocumentFactory


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
            docs=100
        )

    def test_evaluate_dataset_version_pass(self):
        test_version = self.dataset.versions.filter(is_current=False).last()
        fallback_collections = self.dataset.evaluate_dataset_version(test_version)
        self.assertEqual(fallback_collections, [], "Expected identical versions to pass evaluation")
        test_version.document_set.last().delete()
        fallback_collections = self.dataset.evaluate_dataset_version(test_version)
        self.assertEqual(fallback_collections, [], "Expected versions with less than 5% difference to pass evaluation")

        extra_documents = [
            DocumentFactory.create(dataset_version=test_version, collection=test_version.collection_set.last())
            for ix in range(30)
        ]
        test_version.document_set.add(*extra_documents)
        fallback_collections = self.dataset.evaluate_dataset_version(test_version)
        self.assertEqual(fallback_collections, [], "Expected versions with increase of more than 5% to pass evaluation")
                
        self.dataset.versions.update(is_current=False)
        fallback_collections = self.dataset.evaluate_dataset_version(test_version)
        self.assertEqual(fallback_collections, [], "Expected no fallbacks when no promoted previous versions exist")

    def test_evaluate_dataset_version_fail(self):
        fallback_collections = self.dataset.evaluate_dataset_version(DatasetVersionFactory.create(is_current=False))
        self.assertEqual(len(fallback_collections), 1, "Expected empty dataset version to generate fallback")
        self.assertIsInstance(fallback_collections[0], Collection)
        self.assertEqual(fallback_collections[0].name, "test")

        test_version = self.dataset.versions.filter(is_current=False).last()
        for doc in test_version.document_set.all()[:94]:
            doc.delete() 
        fallback_collections = self.dataset.evaluate_dataset_version(test_version)
        self.assertEqual(
            len(fallback_collections), 1,
            "Expected dataset version with insufficient docs to generate fallback"
        )
        self.assertIsInstance(fallback_collections[0], Collection)
        self.assertEqual(fallback_collections[0].name, "test")

    def test_evaluate_dataset_version_old_corrupt_collection(self):
        # First we corrupt a collection by setting dataset_version to None on all documents.
        # And then we'll copy a healthy collection to the test dataset version.
        # This state may get created by the index_dataset_version command.
        test_version = self.dataset.versions.filter(is_current=False).last()
        test_version.document_set.update(dataset_version=None)
        current_version = self.dataset.versions.filter(is_current=True).last()
        current_collection = current_version.collection_set.last()
        test_version.copy_collection(current_collection)
        # In this state we want to ensure that the healthy collection is not seen as erroneous.
        # And the corrupt collection should get ignored.
        fallback_collections = self.dataset.evaluate_dataset_version(test_version)
        self.assertEqual(
            fallback_collections, [],
            "Expected the old corrupt collection to get ignored. "
            "No fallback needed with the new healthy collection in place."
        )

class TestSmallDataset(TestCase):

    def setUp(self):
        super().setUp()
        now = make_aware(datetime.now())
        self.dataset = DatasetFactory()
        create_dataset_version(
            self.dataset, "0.0.1",
            created_at=now,
            include_current=True,
            copies=2,
            docs=50
        )

    def test_evaluate_dataset_version_pass(self):
        test_version = self.dataset.versions.filter(is_current=False).last()
        fallback_collections = self.dataset.evaluate_dataset_version(test_version)
        self.assertEqual(fallback_collections, [], "Expected identical versions to pass evaluation")
        test_version.document_set.last().delete()
        fallback_collections = self.dataset.evaluate_dataset_version(test_version)
        self.assertEqual(fallback_collections, [], "Expected versions with less than 5% difference to pass evaluation")

        extra_documents = [
            DocumentFactory.create(dataset_version=test_version, collection=test_version.collection_set.last())
            for ix in range(30)
        ]
        test_version.document_set.add(*extra_documents)
        fallback_collections = self.dataset.evaluate_dataset_version(test_version)
        self.assertEqual(fallback_collections, [], "Expected versions with increase of more than 5% to pass evaluation")
        
        for doc in test_version.document_set.all()[:45]:
            doc.delete() 
        fallback_collections = self.dataset.evaluate_dataset_version(test_version)
        self.assertEqual(fallback_collections, [], "Expected versions with more than 5% decrease to pass evaluation")

        self.dataset.versions.update(is_current=False)
        fallback_collections = self.dataset.evaluate_dataset_version(test_version)
        self.assertEqual(fallback_collections, [], "Expected no fallbacks when no promoted previous versions exist")
        