from unittest.mock import patch, Mock, call, mock_open, ANY, MagicMock
from django.test import TestCase, override_settings
from PIL import Image

from core.tasks import generate_pdf_preview
from core.tests.factories import DocumentFactory, FileResourceFactory
from core.utils.resources import serialize_resource


def read_content_mock():
    return (None, MagicMock())


@override_settings(BASE_DIR="/home/search-portal")
class PdfPreviewTestCase(TestCase):

    def setUp(self):
        file_resource = FileResourceFactory.create()
        pipeline = {
            "file": serialize_resource(file_resource)
        }
        self.document = DocumentFactory.create(file_type="pdf", pipeline=pipeline)
        super().setUp()

    @patch('core.models.FileResource.content', new_callable=read_content_mock)
    @patch('pdf2image.convert_from_bytes')
    @patch('PIL.Image.open')
    @patch('os.remove')
    @patch('django.core.files.storage.default_storage.save')
    @patch('core.utils.previews.open', new_callable=mock_open(read_data='test'))
    def test_convert_from_bytes_called(self, open_mock, save_mock, os_remove, image_open, pdf_mock, resource_mock):
        generate_pdf_preview(self.document.id, 1)

        pdf_mock.assert_called_with(ANY, single_file=True)

    @patch('core.models.FileResource.content', new_callable=read_content_mock)
    @patch('pdf2image.convert_from_bytes')
    @patch('PIL.Image.open')
    @patch('os.remove')
    @patch('django.core.files.storage.default_storage.save')
    @patch('core.utils.previews.open', new_callable=mock_open(read_data='test'))
    def test_save(self, open_mock, save_mock, os_remove, image_open, pdf_mock, resource_mock):
        generate_pdf_preview(self.document.id, 1)

        open_mock.assert_has_calls([
            call(
                f"/home/search-portal/screenshot-{self.document.id}.png",
                "rb"
            ),
            call(
                f"/home/search-portal/screenshot-{self.document.id}-400x300.png",
                "rb"
            ),
            call(
                f"/home/search-portal/screenshot-{self.document.id}-200x150.png",
                "rb"
            )
        ], any_order=True)

        save_mock.assert_has_calls([
            call(
                f"previews/{self.document.id}/preview.png",
                ANY
            ),
            call(
                f"previews/{self.document.id}/preview-400x300.png",
                ANY
            ),
            call(
                f"previews/{self.document.id}/preview-200x150.png",
                ANY
            )
        ])

    @patch('core.models.FileResource.content', new_callable=read_content_mock)
    @patch('pdf2image.convert_from_bytes')
    @patch('PIL.Image.open')
    @patch('os.remove')
    @patch('django.core.files.storage.default_storage.save')
    @patch('core.utils.previews.open', new_callable=mock_open(read_data='test'))
    def test_writes_preview_url(self, open_mock, save_mock, os_remove, image_open, pdf_mock, resource_mock):
        generate_pdf_preview(self.document.id, 1)

        self.document.refresh_from_db()

        self.assertEqual(self.document.properties["preview_path"], f"previews/{self.document.id}")

    @patch('core.models.FileResource.content', new_callable=read_content_mock)
    @patch('pdf2image.convert_from_bytes')
    @patch('PIL.Image.open')
    @patch('os.remove')
    @patch('django.core.files.storage.default_storage.save')
    @patch('core.utils.previews.open', new_callable=mock_open(read_data='test'))
    def test_generates_thumbnails(self, open_mock, save_mock, os_remove, image_open, pdf_mock, resource_mock):
        resize_mock = Mock()
        image_open.return_value.thumbnail = resize_mock

        generate_pdf_preview(self.document.id, 1)

        resize_mock.assert_has_calls([
            call((400, 300), Image.ANTIALIAS),
            call((200, 150), Image.ANTIALIAS)
        ])

    @patch('core.models.FileResource.content', new_callable=read_content_mock)
    @patch('pdf2image.convert_from_bytes')
    @patch('PIL.Image.open')
    @patch('os.remove')
    @patch('django.core.files.storage.default_storage.save')
    @patch('core.utils.previews.open', new_callable=mock_open(read_data='test'))
    def test_cleanup(self, open_mock, save_mock, os_remove, image_open, pdf_mock, resource_mock):
        resize_mock = Mock()
        image_open.return_value.resize = resize_mock

        generate_pdf_preview(self.document.id, 1)

        os_remove.assert_has_calls([
            call(f"/home/search-portal/screenshot-{self.document.id}.png"),
            call(f"/home/search-portal/screenshot-{self.document.id}-400x300.png"),
            call(f"/home/search-portal/screenshot-{self.document.id}-200x150.png")
        ])
