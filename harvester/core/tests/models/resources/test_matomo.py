from collections import Iterator

from django.test import TestCase

from core.tests.factories.matomo import MatomoVisitsResourceFactory
from core.models import MatomoVisitsResource


class TestMatomoVisitsResource(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        MatomoVisitsResourceFactory.create(is_initial=True)

    def test_iterate_visits(self):
        visits = MatomoVisitsResource.objects.iterate_visits()
        self.assertIsInstance(visits, Iterator, "Expected large data output to be iterated")
        visits = list(visits)
        self.assertEqual(len(visits), 2)

    def test_iterate_visits_include_staff(self):
        visits = MatomoVisitsResource.objects.iterate_visits(include_staff=True)
        self.assertIsInstance(visits, Iterator, "Expected large data output to be iterated")
        visits = list(visits)
        self.assertEqual(len(visits), 3)

    def test_iterate_visits_minimum_actions(self):
        visits = MatomoVisitsResource.objects.iterate_visits(min_actions=5)
        self.assertIsInstance(visits, Iterator, "Expected large data output to be iterated")
        visits = list(visits)
        self.assertEqual(len(visits), 1)

    def test_iterate_visits_filter_custom_events(self):
        filters = {
            "Goal.Download": True
        }
        visits = MatomoVisitsResource.objects.iterate_visits(filter_custom_events=filters)
        self.assertIsInstance(visits, Iterator, "Expected large data output to be iterated")
        visits = list(visits)
        self.assertEqual(len(visits), 1)
        # Non existing events
        filters = {
            "Goaaaaaaaaal.Download": True
        }
        visits = MatomoVisitsResource.objects.iterate_visits(filter_custom_events=filters)
        self.assertIsInstance(visits, Iterator, "Expected large data output to be iterated")
        visits = list(visits)
        self.assertEqual(len(visits), 0)
