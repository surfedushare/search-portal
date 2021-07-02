from unittest.mock import patch

from django.test import TestCase

from core.models import HttpTikaResource


class TestTikaResource(TestCase):

    @patch("core.models.resources.basic.HttpTikaResource._send")
    @patch("core.models.resources.basic.HttpTikaResource.handle_errors")
    def test_aws_url_signatures(self, mock_handle_error, mock_run):
        """
        When using the send method with X-Amz authorization parameters.
        Then we want these parameters to get stripped from the URL.
        Otherwise a new send with the same input (but different authorization) would re-run Tika.
        However these X-Amz parameters should still be used when executing the request.
        """
        test_tika_url = "http://localhost:8000/test?X-Amz-Signature=123abc&X-Amz-Credential=ASIA"
        expected_uri = "localhost:9090/analyze"
        expected_hash = "3aff9963e92374c216d4ce691f7e173b2553b871"
        resource = HttpTikaResource().post(url=test_tika_url)
        resource.close()
        # We check that methods which run the command were called
        # These commands error with the fake input we give them in this test
        self.assertTrue(mock_run.called)
        self.assertTrue(mock_handle_error)
        # Then we check if the resource actually behaved as expected
        self.assertEqual(resource.uri, expected_uri)
        self.assertEqual(resource.data_hash, expected_hash)
        request = resource.request
        self.assertEqual(request["url"], f"http://{expected_uri}")
        # Testing with different AWS credentials which should yield the same instance
        test_tika_url = "http://localhost:8000/test?X-Amz-Signature=123456abcdef&X-Amz-Credential=ASIA2"
        resource_cache = HttpTikaResource().post(url=test_tika_url)
        self.assertEqual(resource_cache.uri, "localhost:9090/analyze")
        self.assertEqual(resource_cache.data_hash, expected_hash)
