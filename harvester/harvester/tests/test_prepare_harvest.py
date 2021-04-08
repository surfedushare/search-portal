from datetime import datetime

from django.conf import settings
from django.test import TestCase
from django.utils.timezone import make_aware

from core.tests.factories import (DatasetFactory, DatasetVersionFactory, HarvestSourceFactory, HarvestFactory,
                                  DocumentFactory, CollectionFactory)
from edurep.tests.factories import EdurepOAIPMHFactory
from sharekit.tests.factories import SharekitMetadataHarvestFactory
from core.constants import Repositories, DeletePolicies, HarvestStages
from core.utils.harvest import prepare_harvest
from core.models import DatasetVersion, Harvest, Collection, Document
from edurep.models import EdurepOAIPMH
from sharekit.models import SharekitMetadataHarvest


class TestPrepareHarvestBase(TestCase):

    dataset = None
    sharekit = None
    wikiwijs = None
    begin_of_time = make_aware(datetime(year=1970, month=1, day=1))

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dataset = DatasetFactory()
        cls.sharekit = HarvestSourceFactory(
            spec="edusources",
            repository=Repositories.SHAREKIT,
            delete_policy=DeletePolicies.NO
        )
        cls.wikiwijs = HarvestSourceFactory(
            name="Wikiwijs Maken",
            spec="wikiwijsmaken",
            repository=Repositories.EDUREP
        )


class TestPrepareHarvestNoHistory(TestPrepareHarvestBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sharekit_harvest = HarvestFactory(
            dataset=cls.dataset,
            stage=HarvestStages.NEW,
            source=cls.sharekit
        )
        cls.wikiwijs_harvest = HarvestFactory(
            dataset=cls.dataset,
            stage=HarvestStages.NEW,
            source=cls.wikiwijs
        )

    def test_prepare_harvest(self):
        prepare_harvest(self.dataset)
        # See if harvest state is correct
        self.assertEqual(Harvest.objects.all().count(), 2)
        self.assertEqual(Harvest.objects.filter(stage=HarvestStages.NEW).count(), 2)
        for harvest in Harvest.objects.filter(stage=HarvestStages.NEW):
            self.assertEqual(harvest.latest_update_at, self.begin_of_time)
            self.assertIsNone(harvest.harvested_at)
        # Check what happened with resources
        self.assertEqual(EdurepOAIPMH.objects.all().count(), 0)
        # Check what happened with Dataset
        self.assertEqual(DatasetVersion.objects.all().count(), 1)
        dataset_version = DatasetVersion.objects.last()
        self.assertTrue(dataset_version.is_current)
        self.assertEqual(dataset_version.version, settings.VERSION)
        self.assertEqual(dataset_version.collection_set.all().count(), 0)
        self.assertEqual(dataset_version.document_set.all().count(), 0)

    def test_prepare_harvest_reset(self):
        prepare_harvest(self.dataset, reset=True)
        # See if harvest state is correct
        self.assertEqual(Harvest.objects.all().count(), 2)
        self.assertEqual(Harvest.objects.filter(stage=HarvestStages.NEW).count(), 2)
        for harvest in Harvest.objects.filter(stage=HarvestStages.NEW):
            self.assertEqual(harvest.latest_update_at, self.begin_of_time)
            self.assertIsNone(harvest.harvested_at)
        # Check what happened with resources
        self.assertEqual(EdurepOAIPMH.objects.all().count(), 0)
        # Check what happened with Dataset
        self.assertEqual(DatasetVersion.objects.all().count(), 1)
        dataset_version = DatasetVersion.objects.last()
        self.assertTrue(dataset_version.is_current)
        self.assertEqual(dataset_version.version, settings.VERSION)
        self.assertEqual(dataset_version.collection_set.all().count(), 0)
        self.assertEqual(dataset_version.document_set.all().count(), 0)


class TestPrepareHarvestHistory(TestPrepareHarvestBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dataset_version = DatasetVersionFactory.create(dataset=cls.dataset)
        for source in [cls.sharekit, cls.wikiwijs]:
            collection = CollectionFactory.create(name=source.spec, dataset_version=cls.dataset_version)
            DocumentFactory.create(collection=collection, dataset_version=cls.dataset_version)
            DocumentFactory.create(collection=collection, dataset_version=cls.dataset_version)
        cls.last_harvest = make_aware(datetime.now())
        cls.sharekit_harvest = HarvestFactory(
            dataset=cls.dataset,
            stage=HarvestStages.COMPLETE,
            source=cls.sharekit,
            harvested_at=cls.last_harvest
        )
        cls.wikiwijs_harvest = HarvestFactory(
            dataset=cls.dataset,
            stage=HarvestStages.BASIC,
            source=cls.wikiwijs,
            harvested_at=cls.last_harvest
        )
        cls.edurep_resource = EdurepOAIPMHFactory.create()
        cls.sharekit_resource = SharekitMetadataHarvestFactory.create()

    def test_prepare_harvest(self):
        prepare_harvest(self.dataset)
        # See if harvest state is correct
        self.assertEqual(Harvest.objects.all().count(), 2)
        self.assertEqual(Harvest.objects.filter(stage=HarvestStages.NEW).count(), 2)
        for harvest in Harvest.objects.filter(stage=HarvestStages.NEW):
            if harvest.source.delete_policy == DeletePolicies.NO:
                self.assertEqual(harvest.latest_update_at, self.begin_of_time)
                self.assertIsNone(harvest.harvested_at)
            else:
                self.assertEqual(harvest.latest_update_at, self.last_harvest)
                self.assertEqual(harvest.harvested_at, self.last_harvest)
        # Check what happened with resources
        self.assertEqual(EdurepOAIPMH.objects.all().count(), 1)
        self.assertEqual(SharekitMetadataHarvest.objects.all().count(), 0)
        # Check what happened with Dataset
        self.assertEqual(DatasetVersion.objects.all().count(), 2)
        self.assertEqual(DatasetVersion.objects.filter(is_current=True).count(), 1)
        dataset_version = DatasetVersion.objects.filter(is_current=True).last()
        self.assertEqual(dataset_version.version, settings.VERSION)
        self.assertEqual(dataset_version.collection_set.all().count(), 1)
        self.assertEqual(dataset_version.document_set.all().count(), 2)
        self.assertEqual(Collection.objects.all().count(), 3, "Expected 2 old + 1 new Collections")
        self.assertEqual(Document.objects.all().count(), 6, "Expected 4 old + 2 new Documents")

    def test_prepare_harvest_reset(self):
        prepare_harvest(self.dataset, reset=True)
        # See if harvest state is correct
        self.assertEqual(Harvest.objects.all().count(), 2)
        self.assertEqual(Harvest.objects.filter(stage=HarvestStages.NEW).count(), 2)
        for harvest in Harvest.objects.filter(stage=HarvestStages.NEW):
            self.assertEqual(harvest.latest_update_at, self.begin_of_time)
            self.assertIsNone(harvest.harvested_at)
        # Check what happened with resources
        self.assertEqual(EdurepOAIPMH.objects.all().count(), 0)
        self.assertEqual(SharekitMetadataHarvest.objects.all().count(), 0)
        # Check what happened with Dataset
        self.assertEqual(DatasetVersion.objects.all().count(), 2)
        self.assertEqual(DatasetVersion.objects.filter(is_current=True).count(), 1)
        dataset_version = DatasetVersion.objects.filter(is_current=True).last()
        self.assertEqual(dataset_version.version, settings.VERSION)
        self.assertEqual(dataset_version.collection_set.all().count(), 0)
        self.assertEqual(dataset_version.document_set.all().count(), 0)
        self.assertEqual(Collection.objects.all().count(), 2, "Expected no new Collections")
        self.assertEqual(Document.objects.all().count(), 4, "Expected no new Documents")

    def test_prepare_harvest_purge(self):
        # Sets Wikiwijs purge_after to the past and force a implicit "reset"
        self.wikiwijs_harvest.purge_after = self.last_harvest
        self.wikiwijs_harvest.save()
        prepare_harvest(self.dataset)
        # See if harvest state is correct
        self.assertEqual(Harvest.objects.all().count(), 2)
        self.assertEqual(Harvest.objects.filter(stage=HarvestStages.NEW).count(), 2)
        for harvest in Harvest.objects.filter(stage=HarvestStages.NEW):
            self.assertEqual(harvest.latest_update_at, self.begin_of_time)
            self.assertIsNone(harvest.harvested_at)
        # Check what happened with resources
        self.assertEqual(EdurepOAIPMH.objects.all().count(), 0)
        self.assertEqual(SharekitMetadataHarvest.objects.all().count(), 0)
        # Check what happened with Dataset
        self.assertEqual(DatasetVersion.objects.all().count(), 2)
        self.assertEqual(DatasetVersion.objects.filter(is_current=True).count(), 1)
        dataset_version = DatasetVersion.objects.filter(is_current=True).last()
        self.assertEqual(dataset_version.version, settings.VERSION)
        self.assertEqual(dataset_version.collection_set.all().count(), 0)
        self.assertEqual(dataset_version.document_set.all().count(), 0)
        self.assertEqual(Collection.objects.all().count(), 2, "Expected no new Collections")
        self.assertEqual(Document.objects.all().count(), 4, "Expected no new Documents")
