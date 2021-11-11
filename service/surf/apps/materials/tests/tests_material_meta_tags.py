from django.conf import settings
from django.test import TestCase, Client
from unittest import skipIf
from unittest.mock import patch

import surf.apps.materials.views as views
from surf.apps.locale.models import Locale


def patched_version_with_material(a, b):
    return [{
        'title': 'foo',
        'description': 'bar'
    }]


def patched_version_without_material(a, b):
    return []


@skipIf(settings.PROJECT == "nppo", "Frontend not enabled for NPPO")
@patch('webpack_loader.loader.WebpackLoader.get_bundle')
class TestMaterialMetaTags(TestCase):

    def setUp(self):
        self.original = views._get_material_by_external_id
        self.client = Client()
        Locale.objects.create(asset="meta-site-description", en="home", nl="thuis")

    def tearDown(self):
        views._get_material_by_external_id = self.original

    def test_contains_material_in_content_tag(self, mock):
        views._get_material_by_external_id = patched_version_with_material
        response = self.client.get(
            "/materialen/edurep_delen:7a8446c7-1dab-46be-8980-bf1009bc1cfa/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<meta content="foo | Edusources" property=og:title>')
        self.assertContains(
            response, '<meta content="bar" property=og:description>')

    def test_contains_material_in_content_tag_for_english(self, mock):
        views._get_material_by_external_id = patched_version_with_material
        response = self.client.get(
            "/en/materials/edurep_delen:7a8446c7-1dab-46be-8980-bf1009bc1cfa/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<meta content="foo | Edusources" property=og:title>')
        self.assertContains(
            response, '<meta content="bar" property=og:description>')

    def test_when_material_not_found(self, mock):
        views._get_material_by_external_id = patched_version_without_material
        response = self.client.get(
            "/materialen/edurep_delen:7a8446c7-1dab-46be-8980-bf1009bc1cfa/")
        self.assertEqual(response.status_code, 404)

    def test_when_other_path(self, mock):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<meta content="Edusources" property=og:title>')
        self.assertContains(response, '<meta content="thuis" property=og:description>')
        response = self.client.get("/en/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<meta content="Edusources" property=og:title>')
        self.assertContains(response, '<meta content="home" property=og:description>')
