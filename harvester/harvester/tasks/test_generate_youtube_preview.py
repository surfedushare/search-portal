from unittest.mock import patch, Mock, call, mock_open, ANY
from django.test import TestCase, override_settings
from PIL import Image

from harvester.tasks import generate_youtube_preview
from core.tests.factories import DocumentFactory


def success_mock():
    return True


class PreviewYoutubeTestCase(TestCase):

    @override_settings(BASE_DIR="/home/search-portal")
    @patch('core.models.YoutubeThumbnailResource.run')
    def test_screenshot_resource_called_properly(self, resource_mock):
        document = DocumentFactory.create(
            url="https://www.youtube.com/watch?v=uqCO6AunQtE&list=PL-J9RGSpAwsTUz3q-4-Iv-v4i4FBO8Avf&index=62",
            from_youtube=True
        )

        generate_youtube_preview(document.id, 1)

        resource_mock.assert_called_once_with(
            "https://www.youtube.com/watch?v=uqCO6AunQtE&list=PL-J9RGSpAwsTUz3q-4-Iv-v4i4FBO8Avf&index=62",
            output=f"screenshot-{document.id}"
        )

    @override_settings(BASE_DIR="/home/search-portal")
    @patch('core.models.YoutubeThumbnailResource.run')
    @patch('core.models.YoutubeThumbnailResource.success', new_callable=success_mock)
    @patch('core.models.YoutubeThumbnailResource.close')
    @patch('PIL.Image.open')
    @patch('os.remove')
    @patch('django.core.files.storage.default_storage.save')
    @patch('core.utils.previews.open', new_callable=mock_open(read_data='test'))
    def test_save(self, open_mock, save_mock, os_remove, image_open, close_mock,
                  screenshot_resource_success, screenshot_resource_run):
        document = DocumentFactory.create(
            url="https://www.youtube.com/watch?v=uqCO6AunQtE&list=PL-J9RGSpAwsTUz3q-4-Iv-v4i4FBO8Avf&index=62",
            from_youtube=True
        )

        generate_youtube_preview(document.id, 1)

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
    @patch('core.models.YoutubeThumbnailResource.run')
    @patch('core.models.YoutubeThumbnailResource.success', new_callable=success_mock)
    @patch('core.models.YoutubeThumbnailResource.close')
    @patch('PIL.Image.open')
    @patch('os.remove')
    @patch('django.core.files.storage.default_storage.save')
    @patch('core.utils.previews.open', new_callable=mock_open(read_data='test'))
    def test_writes_preview_url_to_properties(self, open_mock, save_mock, os_remove, image_open, close_mock,
                                              screenshot_resource_success, screenshot_resource_run):
        document = DocumentFactory.create(
            url="https://www.youtube.com/watch?v=uqCO6AunQtE&list=PL-J9RGSpAwsTUz3q-4-Iv-v4i4FBO8Avf&index=62",
            from_youtube=True
        )

        generate_youtube_preview(document.id, 1)

        document.refresh_from_db()

        self.assertEqual(document.properties["preview_path"], f"previews/{document.id}")

    @override_settings(BASE_DIR="/home/search-portal")
    @patch('core.models.YoutubeThumbnailResource.run')
    @patch('core.models.YoutubeThumbnailResource.success', new_callable=success_mock)
    @patch('core.models.YoutubeThumbnailResource.close')
    @patch('PIL.Image.open')
    @patch('os.remove')
    @patch('django.core.files.storage.default_storage.save')
    @patch('core.utils.previews.open', new_callable=mock_open(read_data='test'))
    def test_generates_thumbnails(self, open_mock, save_mock, os_remove, image_open, close_mock,
                                  screenshot_resource_success, screenshot_resource_run):
        resize_mock = Mock()
        image_open.return_value.thumbnail = resize_mock

        document = DocumentFactory.create(
            url="https://www.youtube.com/watch?v=uqCO6AunQtE&list=PL-J9RGSpAwsTUz3q-4-Iv-v4i4FBO8Avf&index=62",
            from_youtube=True
        )

        generate_youtube_preview(document.id, 1)

        resize_mock.assert_has_calls([
            call((400, 300), Image.ANTIALIAS),
            call((200, 150), Image.ANTIALIAS)
        ])

    @override_settings(BASE_DIR="/home/search-portal")
    @patch('core.models.YoutubeThumbnailResource.get_extension', return_value=".webp")
    @patch('core.models.YoutubeThumbnailResource.run')
    @patch('core.models.YoutubeThumbnailResource.success', new_callable=success_mock)
    @patch('core.models.YoutubeThumbnailResource.close')
    @patch('PIL.Image.open')
    @patch('os.remove')
    @patch('django.core.files.storage.default_storage.save')
    @patch('core.utils.previews.open', new_callable=mock_open(read_data='test'))
    def test_cleanup(self, open_mock, save_mock, os_remove, image_open, close_mock,
                     screenshot_resource_success, screenshot_resource_run, get_extension_mock):
        resize_mock = Mock()
        image_open.return_value.resize = resize_mock

        document = DocumentFactory.create(
            url="https://www.youtube.com/watch?v=uqCO6AunQtE&list=PL-J9RGSpAwsTUz3q-4-Iv-v4i4FBO8Avf&index=62",
            from_youtube=True
        )

        generate_youtube_preview(document.id, 1)

        os_remove.assert_has_calls([
            call(f"screenshot-{document.id}.webp"),
            call(f"/home/search-portal/screenshot-{document.id}.png"),
            call(f"/home/search-portal/screenshot-{document.id}-400x300.png"),
            call(f"/home/search-portal/screenshot-{document.id}-200x150.png")
        ])
