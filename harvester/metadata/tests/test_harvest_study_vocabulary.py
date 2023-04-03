from django.test import TestCase
from django.core.management import call_command
from metadata.models import MetadataValue


class TestHarvestStudyVocabulary(TestCase):

    fixtures = ["initial-study-vocabulary-resources"]

    def test_no_duplicates(self):
        call_command("harvest_study_vocabulary", "--vocabulary=verpleegkunde")
        call_command("harvest_study_vocabulary", "--vocabulary=verpleegkunde")
        total_objects = MetadataValue.objects.count()
        self.assertEqual(total_objects, 390,
                         "When the command runs twice it should not duplicate values.")

    def test_same_number_applied_science(self):
        with self.assertNumQueries(1026):
            call_command("harvest_study_vocabulary", "--vocabulary=applied-science")

    def test_data_contains_right_values(self):
        call_command("harvest_study_vocabulary", "--vocabulary=applied-science")
        value = MetadataValue.objects.get(
            value="http://purl.edustandaard.nl/concept/27aee99f-1b5f-45ba-84e9-4a52c1d46a63")
        self.assertEqual(value.name, "Python")
        self.assertEqual(value.parent.value,
                         "http://purl.edustandaard.nl/concept/982e3b48-90b9-4fbd-9365-04289afe6929")
        self.assertEqual([descendant.name for descendant in value.get_descendants()],
                         ["Biopython", "Data Cleaning with Python", "Data Visualisation with Python",
                          "Machine Learning  with Python", "NumPy", "Pandas", "Python Basics",
                          "SciPy", "Statistics with Python"])
