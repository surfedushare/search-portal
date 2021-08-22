from django.test import TestCase

from datagrowth.exceptions import DGNoContent

from core.models import ExtractionMapping, ExtractionMethod, JSONExtractionField
from sharekit.extraction import SHAREKIT_EXTRACTION_OBJECTIVE, SharekitMetadataExtraction
from sharekit.tests.factories import SharekitMetadataHarvestFactory
from sharekit.models import SharekitMetadataHarvest


class TestSharekitExtractionMapping(TestCase):

    fixtures = ["sharekit-extraction-mapping"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SharekitMetadataHarvestFactory.create_common_sharekit_responses()

    def setUp(self):
        super().setUp()
        self.mapping = ExtractionMapping.objects.last()

    def test_to_objective(self):
        objective = self.mapping.to_objective()
        base_expectation = {
            "@": "$.data",
            "external_id": "$.id",
            "state": SharekitMetadataExtraction.get_record_state
        }
        for key, expectation in base_expectation.items():
            value = objective.pop(key)
            self.assertEqual(value, expectation)
        for key, expectation in SHAREKIT_EXTRACTION_OBJECTIVE.items():
            self.assertEqual(objective[key], expectation)

    def test_invalid_root(self):
        self.mapping.root = "$.lalalalala"
        objective = self.mapping.to_objective()
        extractor = SharekitMetadataExtraction(config={"objective": objective})
        extraction = extractor.extract_from_resource(SharekitMetadataHarvest.objects.first())
        try:
            list(extraction)
            self.fail("Expected invalid root mapping to raise an exception")
        except DGNoContent:
            pass

    def test_invalid_method_field(self):
        ExtractionMethod.objects.filter(method="get_record_state").update(method="does_not_exist")
        try:
            self.mapping.to_objective()
            self.fail("Expected invalid method name to raise an exception")
        except AttributeError:
            pass

    def test_invalid_json_field_property(self):
        JSONExtractionField.objects.filter(path="$.id").update(path="$.does_not_exist")
        objective = self.mapping.to_objective()
        extractor = SharekitMetadataExtraction(config={"objective": objective})
        extraction = extractor.extract_from_resource(SharekitMetadataHarvest.objects.first())
        for result in extraction:
            self.assertIsNone(result["external_id"])

    def test_invalid_json_field_syntax(self):
        JSONExtractionField.objects.filter(path="$.id").update(path="id")
        objective = self.mapping.to_objective()
        extractor = SharekitMetadataExtraction(config={"objective": objective})
        extraction = extractor.extract_from_resource(SharekitMetadataHarvest.objects.first())
        try:
            list(extraction)
            self.fail("Expected invalid path syntax to raise an exception")
        except ValueError:
            pass
