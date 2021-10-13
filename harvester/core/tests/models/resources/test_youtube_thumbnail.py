from django.test import TestCase

from core.models import YoutubeThumbnailResource


class TestYoutubeThumbnailResource(TestCase):

    def test_get_preview_filename(self):
        jpeg_filename = YoutubeThumbnailResource.get_preview_filename(
            "https://i.ytimg.com/vi/cZEclkrS_xY/hqdefault.jpg?"
            "sqp=-oaymwEcCNACELwBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLBzU2IL91e3jXFPvl4LYENzoyvoeg"
        )
        self.assertEqual(jpeg_filename, "cZEclkrS_xY.jpg")
        webp_filename = YoutubeThumbnailResource.get_preview_filename(
            "https://i.ytimg.com/vi_webp/t6tUThsvE4M/maxresdefault.webp"
        )
        self.assertEqual(webp_filename, "t6tUThsvE4M.webp")
