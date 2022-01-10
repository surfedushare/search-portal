from unittest.mock import patch
from datetime import datetime
from time import sleep

from django.test import TestCase
from django.utils.timezone import make_aware

from core.constants import Repositories, HarvestStages
from core.tests.factories import (DatasetFactory, DatasetVersionFactory, CollectionFactory, DocumentFactory,
                                  HarvestFactory, HarvestSourceFactory)
from core.models import Collection, Harvest
from sharekit.tests.factories import SharekitMetadataHarvestFactory
from sharekit.tasks import sync_sharekit_metadata


def create_dataset_data(dataset):
    previous_version = DatasetVersionFactory.create(dataset=dataset, is_current=False)
    current_version = DatasetVersionFactory.create(dataset=dataset, version="0.0.2")
    previous_edusources = CollectionFactory.create(dataset_version=previous_version, name="edusources")
    previous_wikiwijs = CollectionFactory.create(dataset_version=previous_version, name="wikiwijs")
    current_edusources = CollectionFactory.create(dataset_version=current_version, name="edusources")
    current_wikiwijs = CollectionFactory.create(dataset_version=current_version, name="wikiwijs")
    DocumentFactory.create(dataset_version=previous_version, collection=previous_edusources,
                           reference="5be6dfeb-b9ad-41a8-b4f5-94b9438e4257", mime_type="unknown")
    DocumentFactory.create(dataset_version=previous_version, collection=previous_wikiwijs,
                           reference="5be6dfeb-b9ad-41a8-b4f5-94b9438e4257", mime_type="unknown")
    DocumentFactory.create(dataset_version=current_version, collection=current_edusources,
                           reference="5be6dfeb-b9ad-41a8-b4f5-94b9438e4257", mime_type="unknown")
    DocumentFactory.create(dataset_version=current_version, collection=current_wikiwijs,
                           reference="5be6dfeb-b9ad-41a8-b4f5-94b9438e4257", mime_type="unknown")


def create_dataset_harvests(dataset_type, dataset, sources, latest_update_at):
    HarvestFactory.create(  # this gets ignored for inactive datasets
        dataset=dataset,
        source=sources["sharekit"],
        stage=HarvestStages.COMPLETE,
        latest_update_at=latest_update_at
    )
    HarvestFactory.create(  # this always gets ignored
        dataset=dataset,
        source=sources["wikiwijs"],
        stage=HarvestStages.COMPLETE,
        latest_update_at=latest_update_at
    )
    if dataset_type == "primary":
        HarvestFactory.create(  # NEW harvests should get ignored
            dataset=dataset,
            source=sources["sharekit"],
            stage=HarvestStages.NEW,
            latest_update_at=latest_update_at
        )


class TestSyncSharekitMetadata(TestCase):

    def setUp(self):
        super().setUp()
        self.latest_update_at = make_aware(
            datetime(year=2020, month=2, day=10, hour=13, minute=8, second=39, microsecond=315000)
        )
        sources = {
            "sharekit": HarvestSourceFactory(spec="edusources", repository=Repositories.SHAREKIT),
            "sharekit_private": HarvestSourceFactory(spec="edusourcesprivate", repository=Repositories.SHAREKIT),
            "wikiwijs": HarvestSourceFactory(spec="wikiwijsmaken", repository=Repositories.EDUREP)
        }
        datasets = {
            "primary": DatasetFactory.create(name="primary"),
            "inactive": DatasetFactory.create(name="inactive", is_active=False)
        }
        for dataset_type, dataset in datasets.items():
            create_dataset_data(dataset)
            create_dataset_harvests(dataset_type, dataset, sources, self.latest_update_at)
        SharekitMetadataHarvestFactory.create(is_initial=False, number=0, is_restricted=False)
        sleep(1)  # makes sure created_at and modified_at will differ at least 1 second when asserting

    def test_sync_sharekit_metadata(self):
        sync_sharekit_metadata()
        # Checking data updates
        for collection in Collection.objects.filter(name="wikiwijs"):
            self.assertEqual(collection.documents.count(), 1,
                             "Wikiwijs sources should never gain documents through sync_sharekit_metadata")
            doc = collection.documents.last()
            self.assertEqual(
                doc.properties["technical_type"], "unknown",
                "Wikiwijs sources should never get document updates from sync_sharekit_metadata"
            )
            self.assertEqual(doc.created_at.replace(microsecond=0), doc.modified_at.replace(microsecond=0))
        for collection in Collection.objects.filter(dataset_version__dataset__is_active=False):
            self.assertEqual(collection.documents.count(), 1,
                             "Inactive datasets should never gain documents through sync_sharekit_metadata")
            doc = collection.documents.last()
            self.assertEqual(
                doc.properties["technical_type"], "unknown",
                "Inactive datasets should never get document updates from sync_sharekit_metadata"
            )
            self.assertEqual(doc.created_at.replace(microsecond=0), doc.modified_at.replace(microsecond=0))
        for collection in Collection.objects.filter(dataset_version__version="0.0.1"):
            self.assertEqual(collection.documents.count(), 1,
                             "Non-current dataset versions should never gain documents through sync_sharekit_metadata")
            doc = collection.documents.last()
            self.assertEqual(
                doc.properties["technical_type"], "unknown",
                "Non-current dataset versions should never get document updates from sync_sharekit_metadata"
            )
            self.assertEqual(doc.created_at.replace(microsecond=0), doc.modified_at.replace(microsecond=0))
        # See if active dataset did get an update
        dataset_name = "primary"
        for collection in Collection.objects.filter(name="edusources", dataset_version__version="0.0.2",
                                                    dataset_version__dataset__name=dataset_name):
            self.assertEqual(collection.documents.count(), 5,
                             f"Did not add documents to collection inside dataset {dataset_name}")
            update_doc = collection.documents.get(properties__external_id="5be6dfeb-b9ad-41a8-b4f5-94b9438e4257")
            self.assertEqual(update_doc.properties["technical_type"], "website",
                             f"Did not update documents of collection inside dataset {dataset_name}")
            self.assertNotEqual(
                update_doc.created_at.replace(microsecond=0),
                update_doc.modified_at.replace(microsecond=0)
            )
            delete_doc = collection.documents.get(properties__external_id="3903863-6c93-4bda-b850-277f3c9ec00e")
            self.assertEqual(delete_doc.properties["state"], "deleted")
        # Checking harvest instance updates
        for harvest in Harvest.objects.filter(source__spec="wikiwijs"):
            self.assertEqual(
                harvest.latest_update_at, self.latest_update_at,
                "Wikiwijs sources should not get latest_update_at modifications from sync_sharekit_metadata"
            )
        for harvest in Harvest.objects.filter(source__spec="edusources", dataset__is_active=False):
            self.assertEqual(
                harvest.latest_update_at, self.latest_update_at,
                "Inactive sources should not get latest_update_at modifications from sync_sharekit_metadata"
            )
        for harvest in Harvest.objects.exclude(stage=HarvestStages.COMPLETE):
            self.assertEqual(
                harvest.latest_update_at, self.latest_update_at,
                "Non-complete sources should not get latest_update_at modifications from sync_sharekit_metadata"
            )
        for harvest in Harvest.objects.filter(source__spec="edusources", dataset__is_active=True,
                                              stage=HarvestStages.COMPLETE):
            self.assertGreater(
                harvest.latest_update_at, self.latest_update_at,
                "Active Sharekit sources should have higher latest_update_at after sync_sharekit_metadata"
            )

    def test_error_responses(self):
        with patch("sharekit.tasks.send", return_value=([], [1],)):
            sync_sharekit_metadata()
        # Simply test that nothing changed due to the error responses
        for collection in Collection.objects.all():
            self.assertEqual(collection.documents.count(), 1)
            doc = collection.documents.last()
            self.assertEqual(doc.properties["technical_type"], "unknown")
            self.assertEqual(doc.created_at.replace(microsecond=0), doc.modified_at.replace(microsecond=0))
        for harvest in Harvest.objects.all():
            self.assertEqual(harvest.latest_update_at, self.latest_update_at)
