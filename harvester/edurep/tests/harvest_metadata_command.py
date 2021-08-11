from core.tests.commands.harvest_metadata import TestMetadataHarvest, TestMetadataHarvestWithHistory
from core.constants import Repositories
from core.models import HarvestSource, Collection
from edurep.tests.factories import EdurepOAIPMHFactory


class TestMetadataHarvestEdurep(TestMetadataHarvest):

    spec_set = "surfsharekit"
    repository = Repositories.EDUREP

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        EdurepOAIPMHFactory.create_common_edurep_responses()
        sharekit = HarvestSource.objects.get(id=1)
        sharekit.repository = cls.repository
        sharekit.spec = cls.spec_set
        sharekit.save()
        other = HarvestSource.objects.get(id=2)
        other.repository = cls.repository
        other.save()


class TestMetadataHarvestWithHistoryEdurep(TestMetadataHarvestWithHistory):

    spec_set = "surfsharekit"
    repository = Repositories.EDUREP

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        EdurepOAIPMHFactory.create_common_edurep_responses(include_delta=True)
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
            .update(reference="surfsharekit:oai:surfsharekit.nl:5be6dfeb-b9ad-41a8-b4f5-94b9438e4257")
        collection.documents \
            .filter(reference="5af0e26f-c4d2-4ddd-94ab-7dd0bd531751") \
            .update(reference="surfsharekit:oai:surfsharekit.nl:5af0e26f-c4d2-4ddd-94ab-7dd0bd531751")
