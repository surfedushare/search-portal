from unittest.mock import patch
from datetime import timedelta
from time import sleep

from django.test import TestCase

from core.tests.factories import (DatasetFactory, DatasetVersionFactory, CollectionFactory, DocumentFactory,
                                  ElasticIndexFactory)
from core.tests.mocks import get_search_client_mock
from core.models import ElasticIndex
from core.tasks import sync_indices


def create_dataset_data(dataset):
    previous_version = DatasetVersionFactory.create(dataset=dataset, is_current=False)
    current_version = DatasetVersionFactory.create(dataset=dataset, version="0.0.2")
    previous_edusources = CollectionFactory.create(dataset_version=previous_version, name="edusources")
    previous_wikiwijs = CollectionFactory.create(dataset_version=previous_version, name="wikiwijs")
    current_edusources = CollectionFactory.create(dataset_version=current_version, name="edusources")
    current_wikiwijs = CollectionFactory.create(dataset_version=current_version, name="wikiwijs")
    # Dutch documents
    DocumentFactory.create(dataset_version=previous_version, collection=previous_edusources)
    DocumentFactory.create(dataset_version=previous_version, collection=previous_wikiwijs)
    DocumentFactory.create(dataset_version=current_version, collection=current_edusources)
    DocumentFactory.create(dataset_version=current_version, collection=current_wikiwijs)
    sleep(1)  # creates a 1s difference in modified_at datetimes (these are hard to mock with factory_boy)
    DocumentFactory.create(dataset_version=previous_version, collection=previous_edusources,
                           reference="5be6dfeb-b9ad-41a8-b4f5-94b9438e4257")
    DocumentFactory.create(dataset_version=previous_version, collection=previous_wikiwijs,
                           reference="5be6dfeb-b9ad-41a8-b4f5-94b9438e4257")
    DocumentFactory.create(dataset_version=current_version, collection=current_edusources,
                           reference="5be6dfeb-b9ad-41a8-b4f5-94b9438e4257")
    DocumentFactory.create(dataset_version=current_version, collection=current_wikiwijs,
                           reference="5be6dfeb-b9ad-41a8-b4f5-94b9438e4257")
    # English documents
    DocumentFactory.create(dataset_version=previous_version, collection=previous_edusources, language="en")
    DocumentFactory.create(dataset_version=previous_version, collection=previous_wikiwijs, language="en")
    DocumentFactory.create(dataset_version=current_version, collection=current_edusources, language="en")
    DocumentFactory.create(dataset_version=current_version, collection=current_wikiwijs, language="en")
    # Unknown documents
    DocumentFactory.create(dataset_version=previous_version, collection=previous_edusources, language="other")
    DocumentFactory.create(dataset_version=previous_version, collection=previous_wikiwijs, language="other")
    DocumentFactory.create(dataset_version=current_version, collection=current_edusources, language="other")
    DocumentFactory.create(dataset_version=current_version, collection=current_wikiwijs, language="other")

    return current_version, previous_version


def create_dataset_version_indices(dataset_version):
    pushed_at = dataset_version.created_at.replace(microsecond=0) + timedelta(seconds=1)
    for language in ["nl", "en", "unk"]:
        ElasticIndexFactory.create(  # this gets ignored for inactive datasets
            name=f"{dataset_version.dataset.name}-{dataset_version.version}-{dataset_version.id}",
            dataset_version=dataset_version,
            language=language,
            pushed_at=pushed_at,
            configuration={}
        )
    return pushed_at


class TestSyncIndices(TestCase):

    search_client = get_search_client_mock(has_history=True)

    def setUp(self):
        super().setUp()
        datasets = {
            "inactive": DatasetFactory.create(name="inactive", is_active=False),
            "secondary": DatasetFactory.create(name="secondary"),
            "primary": DatasetFactory.create(name="primary"),
        }
        self.pushed_ats = {}
        for dataset_type, dataset in datasets.items():
            dataset_versions = create_dataset_data(dataset)
            for dataset_version in dataset_versions:
                pushed_at = create_dataset_version_indices(dataset_version)
                self.pushed_ats[dataset_version.id] = pushed_at
        sleep(3)

    @patch("core.models.search.index.get_opensearch_client", return_value=search_client)
    @patch("core.models.search.index.streaming_bulk")
    def test_sync_indices(self, streaming_bulk_mock, get_search_client_mock):
        sync_indices()
        # Check if data was send to search engine
        for args, kwargs in streaming_bulk_mock.call_args_list:
            client, docs = args
            index_name, version, version_id, language = kwargs["index"].split("-")
            if language == "nl":
                self.assertEqual(
                    len(list(docs)), 2,
                    "Expected both an edusources and wikwijs Document to get pushed to nl"
                )
            elif language == "en":
                self.assertEqual(
                    len(list(docs)), 2,
                    "Expected both an edusources and wikwijs Document to get pushed to en"
                )
            elif language == "unk":
                self.assertEqual(
                    len(list(docs)), 2,
                    "Expected both an edusources and wikwijs Document to get pushed to unk"
                )
            self.assertEqual(index_name, "primary")
            self.assertEqual(version, "002")
        # Check that pushed_at was updated
        for index in ElasticIndex.objects.filter(name__contains="primary-0.0.2"):
            self.assertGreater(index.pushed_at, self.pushed_ats[index.dataset_version_id])
        for index in ElasticIndex.objects.exclude(name__contains="primary-0.0.2"):
            self.assertEqual(index.pushed_at, self.pushed_ats[index.dataset_version_id],
                             "Only the latest DatasetVersions of the newest Dataset should get pushed")

    @patch("core.models.search.index.get_opensearch_client", return_value=search_client)
    @patch("core.models.search.index.streaming_bulk")
    def test_sync_indices_new(self, streaming_bulk_mock, get_search_client_mock):
        ElasticIndex.objects.update(pushed_at=None)  # this makes all indices look like they're just created
        sync_indices()
        self.assertEqual(streaming_bulk_mock.call_count, 0)
        for index in ElasticIndex.objects.all():
            self.assertIsNone(index.pushed_at)
