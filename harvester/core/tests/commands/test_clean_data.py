from unittest.mock import patch
from datetime import datetime, timedelta

from django.test import TestCase
from django.core.management import call_command
from django.utils.timezone import make_aware

from core.models import Document, HttpTikaResource, DatasetVersion, Collection, Dataset, ElasticIndex
from core.tests.mocks import get_elastic_client_mock
from core.tests.factories import DatasetFactory, create_dataset_version


class TestCleanData(TestCase):

    elastic_client = get_elastic_client_mock(has_history=True)

    def setUp(self):
        super().setUp()
        self.active_dataset = DatasetFactory.create(name="active test", is_active=True)
        created_time = make_aware(datetime.now())
        for version_number in range(0, 29, 7):
            created_time -= timedelta(days=version_number)
            create_dataset_version(self.active_dataset, f"0.0.{28 - version_number}", created_time)
        self.inactive_dataset = DatasetFactory.create(name="inactive test", is_active=False)
        created_time = make_aware(datetime.now())
        for version_number in range(21, 43, 7):
            created_time -= timedelta(days=version_number)
            create_dataset_version(self.inactive_dataset, f"0.0.{42 - version_number}", created_time)

    @patch("core.models.search.index.get_es_client", return_value=elastic_client)
    def test_clean_data(self, get_es_client):
        get_es_client.reset_mock()
        call_command("clean_data")
        # Assert which data remains
        self.assertEqual(Dataset.objects.count(), 2, "clean_data should never delete Datasets")
        self.assertEqual(DatasetVersion.objects.filter(is_current=False).count(), 4,
                         "Per dataset only younger than DATA_RETENTION_PURGE_AFTER of non-currents should remain")
        self.assertEqual(
            DatasetVersion.objects.filter(is_current=True).count(), 2 + 2,
            "Expected two current DatasetVersion younger than DATA_RETENTION_PURGE_AFTER and "
            "DATA_RETENTION_KEEP_VERSIONS current DatasetVersions per Dataset extra"
        )
        self.assertEqual(ElasticIndex.objects.count(), 16, "Expected two indices per dataset version")
        self.assertEqual(Collection.objects.count(), 8, "Expected one collection per dataset version")
        self.assertEqual(Document.objects.count(), 40, "Expected five documents per collection")
        self.assertEqual(HttpTikaResource.objects.count(), 40, "Expected one HttpTikaResource per Document")
        # Check if Elastic indices were removed properly as well
        self.assertEqual(get_es_client.call_count, 76, "Not sure why there are two calls per removed ElasticIndex")
        self.assertEqual(self.elastic_client.indices.exists.call_count, 38)
        self.assertEqual(self.elastic_client.indices.delete.call_count, 38)

    def test_clean_data_duplicated_resources(self):
        # We'll add old Resources to new Documents and make sure these resources do not get deleted
        oldest_version = DatasetVersion.objects.last()  # will get removed
        newest_version = DatasetVersion.objects.first()  # will remain
        old_tika_ids = []
        new_tika_ids = []
        for old_doc, new_doc in zip(oldest_version.document_set.all(), newest_version.document_set.all()):
            old_tika_ids.append(old_doc.pipeline["tika"]["id"])
            new_tika_ids.append(new_doc.pipeline["tika"]["id"])
            new_doc.properties = old_doc.properties
            new_doc.save()
        self.assertEqual(HttpTikaResource.objects.filter(id__in=old_tika_ids).count(), len(old_tika_ids),
                         "Old HttpTikaResource should remain, because new Documents use them")
        self.assertEqual(HttpTikaResource.objects.filter(id__in=new_tika_ids).count(), len(new_tika_ids),
                         "New HttpTikaResource without Document should remain, because they are new")

    @patch("core.models.search.index.get_es_client", return_value=elastic_client)
    def test_clean_data_missing_resources(self, get_es_client):
        # We'll remove all resources. This should not interfere with deletion of other data
        HttpTikaResource.objects.all().delete()
        get_es_client.reset_mock()
        call_command("clean_data")
        # Assert which data remains
        self.assertEqual(Dataset.objects.count(), 2, "clean_data should never delete Datasets")
        self.assertEqual(DatasetVersion.objects.filter(is_current=False).count(), 4,
                         "Per dataset only younger than DATA_RETENTION_PURGE_AFTER of non-currents should remain")
        self.assertEqual(
            DatasetVersion.objects.filter(is_current=True).count(), 2 + 2,
            "Expected two current DatasetVersion younger than DATA_RETENTION_PURGE_AFTER and "
            "DATA_RETENTION_KEEP_VERSIONS current DatasetVersions per Dataset extra"
        )
        self.assertEqual(ElasticIndex.objects.count(), 16, "Expected two indices per dataset version")
        self.assertEqual(Collection.objects.count(), 8, "Expected one collection per dataset version")
        self.assertEqual(Document.objects.count(), 40, "Expected five documents per collection")
        self.assertEqual(HttpTikaResource.objects.count(), 0)
        # Check if Elastic indices were removed properly as well
        self.assertEqual(get_es_client.call_count, 76, "Not sure why there are two calls per removed ElasticIndex")
        self.assertEqual(self.elastic_client.indices.exists.call_count, 38)
        self.assertEqual(self.elastic_client.indices.delete.call_count, 38)
