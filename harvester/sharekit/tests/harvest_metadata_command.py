from core.tests.commands.harvest_metadata import TestMetadataHarvest, TestMetadataHarvestWithHistory
from core.constants import Repositories
from sharekit.tests.factories import SharekitMetadataHarvestFactory


class TestMetadataHarvestSharekit(TestMetadataHarvest):

    spec_set = "edusources"
    repository = Repositories.SHAREKIT

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SharekitMetadataHarvestFactory.create_common_sharekit_responses()


class TestMetadataHarvestWithHistorySharekit(TestMetadataHarvestWithHistory):

    spec_set = "edusources"
    repository = Repositories.SHAREKIT

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SharekitMetadataHarvestFactory.create_common_sharekit_responses(include_delta=True)
