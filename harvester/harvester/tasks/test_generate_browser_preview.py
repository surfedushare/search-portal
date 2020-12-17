from unittest.mock import patch, Mock, call, mock_open, ANY
from django.test import TestCase, override_settings
from PIL import Image

from harvester.tasks import generate_browser_preview
from core.tests.factories import DocumentFactory


def success_mock():
    return True


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
    @patch('core.models.ChromeScreenshotResource.run')
    @patch('core.models.ChromeScreenshotResource.success', new_callable=success_mock)
    @patch('core.models.ChromeScreenshotResource.close')
    @patch('PIL.Image.open')
    @patch('os.remove')
    @patch('django.core.files.storage.default_storage.save')
    @patch('core.utils.previews.open', new_callable=mock_open(read_data='test'))
    def test_save(self, open_mock, save_mock, os_remove, image_open, close_mock,
                  screenshot_resource_success, screenshot_resource_run):
        document = DocumentFactory.create()

        generate_browser_preview(document.id)

        open_mock.assert_has_calls([
            call(
                f"/home/search-portal/screenshot-{document.id}.png",
                "rb"
            ),
            call(
                f"/home/search-portal/screenshot-{document.id}-400x300.png",
                "rb"
            ),
            call(
                f"/home/search-portal/screenshot-{document.id}-200x150.png",
                "rb"
            )
        ], any_order=True)

        save_mock.assert_has_calls([
            call(
                f"previews/{document.id}/preview.png",
                ANY
            ),
            call(
                f"previews/{document.id}/preview-400x300.png",
                ANY
            ),
            call(
                f"previews/{document.id}/preview-200x150.png",
                ANY
            )
        ])

    @override_settings(BASE_DIR="/home/search-portal")
    @patch('core.models.ChromeScreenshotResource.run')
    @patch('core.models.ChromeScreenshotResource.success', new_callable=success_mock)
    @patch('core.models.ChromeScreenshotResource.close')
    @patch('PIL.Image.open')
    @patch('os.remove')
    @patch('django.core.files.storage.default_storage.save')
    @patch('core.utils.previews.open', new_callable=mock_open(read_data='test'))
    def test_writes_preview_url_to_properties(self, open_mock, save_mock, os_remove, image_open, close_mock,
                                              screenshot_resource_success, screenshot_resource_run):
        document = DocumentFactory.create()

        generate_browser_preview(document.id)

        document.refresh_from_db()

        self.assertEqual(document.properties["preview_path"], f"previews/{document.id}")

    @override_settings(BASE_DIR="/home/search-portal")
    @patch('core.models.ChromeScreenshotResource.run')
    @patch('core.models.ChromeScreenshotResource.success', new_callable=success_mock)
    @patch('core.models.ChromeScreenshotResource.close')
    @patch('PIL.Image.open')
    @patch('os.remove')
    @patch('django.core.files.storage.default_storage.save')
    @patch('core.utils.previews.open', new_callable=mock_open(read_data='test'))
    def test_generates_thumbnails(self, open_mock, save_mock, os_remove, image_open, close_mock,
                                  screenshot_resource_success, screenshot_resource_run):
        resize_mock = Mock()
        image_open.return_value.thumbnail = resize_mock

        document = DocumentFactory.create()

        generate_browser_preview(document.id)

        resize_mock.assert_has_calls([
            call((400, 300), Image.ANTIALIAS),
            call((200, 150), Image.ANTIALIAS)
        ])

    @override_settings(BASE_DIR="/home/search-portal")
    @patch('core.models.ChromeScreenshotResource.run')
    @patch('core.models.ChromeScreenshotResource.success', new_callable=success_mock)
    @patch('core.models.ChromeScreenshotResource.close')
    @patch('PIL.Image.open')
    @patch('os.remove')
    @patch('django.core.files.storage.default_storage.save')
    @patch('core.utils.previews.open', new_callable=mock_open(read_data='test'))
    def test_cleanup(self, open_mock, save_mock, os_remove, image_open, close_mock,
                     screenshot_resource_success, screenshot_resource_run):
        resize_mock = Mock()
        image_open.return_value.resize = resize_mock

        document = DocumentFactory.create()

        generate_browser_preview(document.id)

        os_remove.assert_has_calls([
            call(f"/home/search-portal/screenshot-{document.id}.png"),
            call(f"/home/search-portal/screenshot-{document.id}-400x300.png"),
            call(f"/home/search-portal/screenshot-{document.id}-200x150.png")
        ])
