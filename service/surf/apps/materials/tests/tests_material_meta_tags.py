from django.test import SimpleTestCase, Client
from unittest.mock import patch

import surf.apps.materials.views as views


def patched_version_with_material(a, b):
    return [{
        'title': 'foo',
        'description': 'bar'
    }]


def patched_version_without_material(a, b):
    return []


@patch('webpack_loader.loader.WebpackLoader.get_bundle')
class TestMaterialMetaTags(SimpleTestCase):
    def setUp(self):
        self.original = views._get_material_by_external_id
        self.client = Client()

    def tearDown(self):
        views._get_material_by_external_id = self.original

    def test_contains_material_in_content_tag(self, mock):
        views._get_material_by_external_id = patched_version_with_material
        response = self.client.get(
            "/materialen/edurep_delen:7a8446c7-1dab-46be-8980-bf1009bc1cfa/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<meta content="foo" property=og:title>')
        self.assertContains(
            response, '<meta content="bar" property=og:description>')

    def test_contains_material_in_content_tag_for_english(self, mock):
        views._get_material_by_external_id = patched_version_with_material
        response = self.client.get(
            "/en/materials/edurep_delen:7a8446c7-1dab-46be-8980-bf1009bc1cfa/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<meta content="foo" property=og:title>')
        self.assertContains(
            response, '<meta content="bar" property=og:description>')

    def test_when_material_not_found(self, mock):
        views._get_material_by_external_id = patched_version_without_material
        response = self.client.get(
            "/materialen/edurep_delen:7a8446c7-1dab-46be-8980-bf1009bc1cfa/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<meta content="SURF | edusources" property=og:title>')
        self.assertContains(
            response, '<meta content="Edusources" property=og:description>')

    def test_when_other_path(self, mock):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<meta content="SURF | edusources" property=og:title>')
        self.assertContains(
            response, '<meta content="Edusources" property=og:description>')
