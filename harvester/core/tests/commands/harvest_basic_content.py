import os
from unittest.mock import patch
from io import StringIO
from datetime import datetime

from django.test import TestCase, override_settings
from django.core.management import call_command
from django.utils.timezone import make_aware

from core.constants import HarvestStages
from core.models import OAIPMHHarvest
from core.management.commands.harvest_basic_content import Command as BasicHarvestCommand


GET_EDUREP_OAIPMH_SEEDS_TARGET = "core.management.commands.harvest_basic_content.get_edurep_oaipmh_seeds"
DOWNLOAD_SEED_FILES_TARGET = "core.management.commands.harvest_basic_content.Command.download_seed_files"
EXTRACT_FROM_SEEDS_TARGET = "core.management.commands.harvest_basic_content.Command.extract_from_seed_files"
SEND_SERIE_TARGET = "core.management.commands.harvest_basic_content.send_serie"
RUN_SERIE_TARGET = "core.management.commands.harvest_basic_content.run_serie"
GENERATE_PRESIGNED_URL_TARGET = "core.models.resources.basic.s3_client.generate_presigned_url"
DUMMY_SEEDS = [
    {"state": "dummy", "url": "https://www.vn.nl/speciaalmelk-rechtstreeks-koe/", "mime_type": "text/html"},
    {"state": "dummy", "url": "http://www.samhao.nl/webopac/MetaDataEditDownload.csp?file=2:145797:1", "mime_type": "application/pdf"}
]


def generate_presigned_url(permission, Params, ExpiresIn):
    return os.path.join("https://test-bucket-name.s3.amazonaws.com", Params["Key"])


class TestBasicHarvest(TestCase):

    fixtures = ["datasets-new", "surf-oaipmh-1970-01-01", "resources"]

    def get_command_instance(self):
        command = BasicHarvestCommand()
        command.show_progress = False
        command.info = lambda x: x
        return command

    @patch(GET_EDUREP_OAIPMH_SEEDS_TARGET, return_value=DUMMY_SEEDS)
    @patch(DOWNLOAD_SEED_FILES_TARGET, return_value=[1])
    @patch(EXTRACT_FROM_SEEDS_TARGET)
    def test_basic_surf(self, extract_target, download_target, seeds_target):
        # Checking whether end result of the command returned by "handle" matches expectations.
        # We'd expect the command to get seeds from get_edurep_oaipmh_seeds function.
        # After that the heavy lifting is done by two methods named download_seed_files and extract_from_seed_files.
        # We'll test those separately, but check if they get called with the seeds returned by get_edurep_oaipmh_seeds
        out = StringIO()
        call_command("harvest_basic_content", "--dataset=test", "--no-progress", "--no-logger", stdout=out)
        # Asserting usage of get_edurep_oaipmh_seeds
        seeds_target.assert_called_once_with(
            "surf", make_aware(datetime(year=1970, month=1, day=1)),
            include_deleted=False
        )
        # Asserting usage of download_seed_files
        download_target.assert_called_once_with(DUMMY_SEEDS)
        # And then usage of extract_from_seeds
        extract_target.assert_called_once_with(DUMMY_SEEDS, [1])
        # Last but not least we check that the correct EdurepHarvest objects have indeed progressed
        # to prevent repetitious harvests.
        surf_harvest = OAIPMHHarvest.objects.get(source__spec="surf")
        self.assertEqual(
            surf_harvest.stage,
            HarvestStages.BASIC,
            "surf set harvest should got updated to stage BASIC to prevent re-harvest in the future"
        )
        edurep_delen_harvest = OAIPMHHarvest.objects.get(source__spec="edurep_delen")
        self.assertEqual(
            edurep_delen_harvest.stage,
            HarvestStages.VIDEO,
            "edurep_delen set harvest got updated to other than VIDEO while we expected it to be ignored"
        )

    def test_basic_invalid_dataset(self):
        # Testing the case where a Dataset does not exist at all
        try:
            call_command("harvest_basic_content", "--dataset=invalid")
            self.fail("harvest_edurep_seeds did not raise for an invalid dataset")
        except OAIPMHHarvest.DoesNotExist:
            pass
        # Testing the case where a Dataset exists, but no harvest tasks are present
        surf_harvest = OAIPMHHarvest.objects.get(source__spec="surf")
        surf_harvest.stage = HarvestStages.BASIC
        surf_harvest.save()
        try:
            call_command("harvest_basic_content", "--dataset=invalid")
            self.fail("harvest_basic_content did not raise for a dataset without pending harvests")
        except OAIPMHHarvest.DoesNotExist:
            pass

    def test_download_seed_files(self):
        # Asserting Datagrowth usage for downloading files.
        # This handles many edge cases for us.
        command = self.get_command_instance()
        with patch(SEND_SERIE_TARGET, return_value=[[12024, 12025], []]) as send_serie_mock:
            command.download_seed_files(DUMMY_SEEDS)
        self.assertEqual(send_serie_mock.call_count, 1, "More than 1 call to send_serie?")
        args, kwargs = send_serie_mock.call_args
        config = kwargs["config"]
        self.assertEqual(config.resource, "core.FileResource", "Wrong resource used for downloading files")
        self.assertEqual(
            args,
            (
                [
                    ['https://www.vn.nl/speciaalmelk-rechtstreeks-koe/'],
                    ['http://www.samhao.nl/webopac/MetaDataEditDownload.csp?file=2:145797:1']
                ],
                [{}, {}],
            ),
            "Wrong arguments given to send_serie processing multiple core.FileResource")
        self.assertEqual(kwargs["method"], "get", "core.FileResource is not using HTTP GET method")

    @override_settings(AWS_STORAGE_BUCKET_NAME="test-bucket-name")
    @patch(GENERATE_PRESIGNED_URL_TARGET, side_effect=generate_presigned_url)
    def test_extract_from_seed_files_s3(self, generate_presigned_url_mock):
        # Asserting Datagrowth usage for extracting content from files with Tika.
        # This handles many edge cases for us.
        # The test also mocks the generate_presigned_url method on the S3 client.
        # We're expecting that client to return a signed URL that Tika can use without getting 403's,
        command = self.get_command_instance()
        with patch(RUN_SERIE_TARGET, return_value=[[1, 2], []]) as send_serie_mock:
            command.extract_from_seed_files(DUMMY_SEEDS, [12024, 12025])
        self.assertEqual(send_serie_mock.call_count, 1, "More than 1 call to send_serie?")
        args, kwargs = send_serie_mock.call_args
        config = kwargs["config"]
        self.assertEqual(config.resource, "core.TikaResource", "Wrong resource used for extracting content")
        s3_url = "https://test-bucket-name.s3.amazonaws.com/"  # a fake URL
        self.assertEqual(
            args,
            (
                [
                    [s3_url + "core/downloads/7/c7/20191209102536078995.index.html"],
                    [s3_url + "core/downloads/f/03/20191209102536508370.MetaDataEditDownload.csp"]
                ],
                [{}, {}],
            ),
            "Wrong arguments given to send_serie processing multiple core.TikaResource"
        )
        self.assertEqual(generate_presigned_url_mock.call_count, 2)
        args, kwargs = generate_presigned_url_mock.call_args
        self.assertEqual(kwargs["ExpiresIn"], 7200, "Expected presigned URL's to expire in two hours")

    def test_extract_from_seed_files_local(self):
        # Asserting extracting content from files with Tika on localhost.
        # Not strictly necessary, but convenient to keep around as it was already here
        command = self.get_command_instance()
        with patch(RUN_SERIE_TARGET, return_value=[[1, 2], []]) as send_serie_mock:
            command.extract_from_seed_files(DUMMY_SEEDS, [12024, 12025])
        self.assertEqual(send_serie_mock.call_count, 1, "More than 1 call to send_serie?")
        args, kwargs = send_serie_mock.call_args
        config = kwargs["config"]
        self.assertEqual(config.resource, "core.TikaResource", "Wrong resource used for extracting content")
        localhost = "http://localhost:8000/media/harvester/"
        self.assertEqual(
            args,
            (
                [
                    [localhost + "core/downloads/7/c7/20191209102536078995.index.html"],
                    [localhost + "core/downloads/f/03/20191209102536508370.MetaDataEditDownload.csp"]
                ],
                [{}, {}],
            ),
            "Wrong arguments given to send_serie processing multiple core.TikaResource"
        )
