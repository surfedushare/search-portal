from unittest.mock import patch, Mock
from django.test import TestCase, override_settings

from harvester.tasks.preview import generate_browser_preview
from core.tests.factories import DocumentFactory


class PreviewTestCase(TestCase):

    @override_settings(BASE_DIR="/home/search-portal")
    @patch('core.models.ChromeScreenshotResource.run')
    def test_screenshot_resource_called_properly(self, screenshot_mock):
        document = DocumentFactory.create(url="https://maken.wikiwijs.nl/124977/Zorgwekkend_gedrag___kopie_1")

        generate_browser_preview(document.id)

        screenshot_mock.assert_called_once_with(
            "https://maken.wikiwijs.nl/124977/Zorgwekkend_gedrag___kopie_1",
            screenshot=f"/home/search-portal/screenshot-{document.id}.png"
        )

    @override_settings(BASE_DIR="/home/search-portal")
    @override_settings(AWS_PREVIEWS_BUCKET_NAME="preview-bucket")
    @patch('core.models.ChromeScreenshotResource.run')
    @patch('core.models.ChromeScreenshotResource.success', return_value=True)
    @patch('core.models.ChromeScreenshotResource.close')
    @patch('boto3.client')
    def test_uploaded_to_s3(self, s3_client, close_mock, screenshot_resource_success, screenshot_resource_run):
        upload_mock = s3_client.return_value.upload_file = Mock()
        document = DocumentFactory.create()

        generate_browser_preview(document.id)

        s3_client.assert_called_once_with("s3")
        upload_mock.assert_called_once_with(
            f"/home/search-portal/screenshot-{document.id}.png",
            "preview-bucket",
            f"previews/{document.id}/preview.png"
        )

    @override_settings(BASE_DIR="/home/search-portal")
    @override_settings(AWS_PREVIEWS_BUCKET_NAME=None)
    @patch('core.models.ChromeScreenshotResource.run')
    @patch('core.models.ChromeScreenshotResource.success', return_value=True)
    @patch('core.models.ChromeScreenshotResource.close')
    @patch('boto3.client')
    def test_not_uploaded_to_s3(self, s3_client, close_mock, screenshot_resource_success, screenshot_resource_run):
        document = DocumentFactory.create()

        generate_browser_preview(document.id)

        s3_client.assert_not_called()

    @override_settings(BASE_DIR="/home/search-portal")
    @override_settings(AWS_PREVIEWS_BUCKET_NAME=None)
    @patch('core.models.ChromeScreenshotResource.run')
    @patch('core.models.ChromeScreenshotResource.success', return_value=True)
    @patch('core.models.ChromeScreenshotResource.close')
    def test_writes_preview_url_to_properties(self, close_mock, screenshot_resource_success, screenshot_resource_run):
        document = DocumentFactory.create()

        generate_browser_preview(document.id)

        document.refresh_from_db()

        self.assertEqual(document.properties["preview_path"], f"previews/{document.id}/preview.png")
