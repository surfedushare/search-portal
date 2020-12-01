from unittest.mock import patch

from django.test import TestCase

from core.models import TikaResource


class TestTikaResource(TestCase):

    fixtures = ["resources"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.instance = TikaResource.objects.get(id=74)

    @patch("core.models.resources.basic.TikaResource._run")
    @patch("core.models.resources.basic.TikaResource.handle_errors")
    def test_aws_url_signatures(self, mock_handle_error, mock_run):
        """
        When using the run method with X-Amz authorization parameters.
        Then we want these parameters to get stripped from the URI.
        Otherwise a new run with the same input (but different authorization) would re-run Tika.
        However these X-Amz parameters should still be used when executing the command.
        """
        test_tika_url = "http://localhost:8000/test?X-Amz-Signature=123abc&X-Amz-Credential=ASIA"
        resource = TikaResource().run(test_tika_url)
        resource.close()
        # We check that methods which run the command were called
        # These commands error with the fake input we give them in this test
        self.assertTrue(mock_run.called)
        self.assertTrue(mock_handle_error)
        # Then we check if the resource actually behaved as expected
        self.assertEqual(
            resource.uri,
            "java -J -jar -t http://localhost:8000/test tika-app-1.24.1.jar",
            "Expected the URI to exclude any X-Amz parameters"
        )
        command = resource.command
        self.assertEqual(command["args"][-1], test_tika_url, "Expected the args to exactly match the input")
        self.assertEqual(command["cmd"][-1], test_tika_url, "Expected the command to include X-Amz parameters")
