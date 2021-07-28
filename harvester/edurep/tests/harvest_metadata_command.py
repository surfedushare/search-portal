from core.tests.commands.harvest_metadata import TestMetadataHarvest, TestMetadataHarvestWithHistory
from core.constants import Repositories
from edurep.tests.factories import EdurepOAIPMHFactory


class TestMetadataHarvestEdurep(TestMetadataHarvest):

    spec_set = "surfsharekit"
    repository = Repositories.EDUREP

    def setUp(self):
        EdurepOAIPMHFactory.create_common_edurep_responses()
        super().setUp()


class TestMetadataHarvestWithHistoryEdurep(TestMetadataHarvestWithHistory):

    spec_set = "surfsharekit"
    repository = Repositories.EDUREP

    def setUp(self):
        EdurepOAIPMHFactory.create_common_edurep_responses(include_delta=True)
        super().setUp()
