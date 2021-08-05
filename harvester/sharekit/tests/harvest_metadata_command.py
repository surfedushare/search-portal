from core.tests.commands.harvest_metadata import TestMetadataHarvest, TestMetadataHarvestWithHistory
from core.constants import Repositories
from core.models import HarvestSource, Collection
from sharekit.tests.factories import SharekitMetadataHarvestFactory


class TestMetadataHarvestSharekit(TestMetadataHarvest):

    spec_set = "edusources"
    repository = Repositories.SHAREKIT

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SharekitMetadataHarvestFactory.create_common_sharekit_responses()
        sharekit = HarvestSource.objects.get(id=1)
        sharekit.repository = cls.repository
        sharekit.spec = cls.spec_set
        sharekit.save()
        other = HarvestSource.objects.get(id=2)
        other.repository = cls.repository
        other.save()

    def setUp(self):
        super().setUp()


class TestMetadataHarvestWithHistorySharekit(TestMetadataHarvestWithHistory):

    spec_set = "edusources"
    repository = Repositories.SHAREKIT

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SharekitMetadataHarvestFactory.create_common_sharekit_responses(include_delta=True)
        sharekit = HarvestSource.objects.get(id=1)
        sharekit.repository = cls.repository
        sharekit.spec = cls.spec_set
        sharekit.save()
        other = HarvestSource.objects.get(id=2)
        other.repository = cls.repository
        other.save()
        collection = Collection.objects.get(id=171)
        collection.name = cls.spec_set
        collection.save()
        collection.documents \
            .filter(properties__title="Using a Vortex | Wageningen UR") \
            .update(reference="5be6dfeb-b9ad-41a8-b4f5-94b9438e4257")

    def setUp(self):
        super().setUp()
