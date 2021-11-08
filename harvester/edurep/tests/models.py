from datetime import datetime
from urllib.parse import unquote
from unittest.mock import patch

from django.test import TestCase
from django.utils.timezone import make_aware
from django.core.exceptions import ValidationError

from datagrowth.exceptions import DGHttpError50X, DGHttpError40X
from edurep.models import EdurepOAIPMH
from edurep.tests.factories import EdurepOAIPMHFactory


class TestEdurepOAIPMH(TestCase):

    @classmethod
    def setUp(cls):
        cls.instance = EdurepOAIPMH()

    @patch("edurep.models.EdurepOAIPMH.handle_errors")
    @patch("edurep.models.EdurepOAIPMH._send")
    def test_get_since_time(self, send_mock, handle_errors_mock):
        self.instance.get("surfsharekit", "2021-01-01T01:00:00Z")
        self.assertEqual(send_mock.call_count, 1)
        self.assertEqual(handle_errors_mock.call_count, 1)
        self.assertEqual(self.instance.uri,
                         "staging.edurep.kennisnet.nl/edurep/oai?"
                         "from=2021-01-01T01%3A00%3A00Z&metadataPrefix=lom&set=surfsharekit&verb=ListRecords")
        self.assertEqual(self.instance.since, make_aware(datetime(year=2021, month=1, day=1, hour=1)))
        self.assertEqual(self.instance.set_specification, "surfsharekit")

    @patch("edurep.models.EdurepOAIPMH.handle_errors")
    @patch("edurep.models.EdurepOAIPMH._send")
    def test_get_since_date(self, send_mock, handle_errors_mock):
        self.instance.get("surfsharekit", "2021-01-01")
        self.assertEqual(send_mock.call_count, 1)
        self.assertEqual(handle_errors_mock.call_count, 1)
        self.assertEqual(self.instance.uri,
                         "staging.edurep.kennisnet.nl/edurep/oai?"
                         "from=2021-01-01&metadataPrefix=lom&set=surfsharekit&verb=ListRecords")
        self.assertEqual(self.instance.since, make_aware(datetime(year=2021, month=1, day=1)))
        self.assertEqual(self.instance.set_specification, "surfsharekit")

    def test_invalid_input(self):
        try:
            self.instance.get()
            self.fail("EdurepOAIPMH did not raise when getting no input")
        except ValidationError:
            pass
        try:
            self.instance.get("surfsharekit", "not-a-time-at-all!")
            self.fail("EdurepOAIPMH did not raise when getting invalid datetime")
        except ValidationError:
            pass

    def test_create_next_request(self):
        previous = EdurepOAIPMHFactory()
        next_request = previous.create_next_request()
        self.assertEqual(
            unquote(next_request["url"]),
            "https://staging.edurep.kennisnet.nl/edurep/oai"
            "?verb=ListRecords&resumptionToken=c1576069959151499|u|f1970-01-01T00:00:00Z|mlom|ssurf"
        )

    def test_handle_errors(self):
        # We'll handle a few cases here:
        # Something very bad with no response at all
        try:
            self.instance.handle_errors()
            self.fail("Empty EdurepOAIPMH did not indicate any kind of network error")
        except DGHttpError50X:
            pass
        # Something wrong with the request
        # Note that this returns 200 and we transform this into something sensible,
        # but we simply fake such a response here
        try:
            self.instance.status = 200
            self.instance.head = {
                "content-type": "text/xml"
            }
            self.instance.body = '<error code="badArgument"></error>'
            self.instance.handle_errors()
            self.fail("EdurepOAIPMH did not raise after receiving a badArgument error")
        except DGHttpError40X:
            self.assertEqual(self.instance.status, 400)
        # Empty response
        # Note that this returns 200 and we transform this into something sensible,
        # but we simply fake such a response here
        self.instance.status = 200
        self.instance.head = {
            "content-type": "text/xml"
        }
        self.instance.body = '<error code="noRecordsMatch"></error>'
        self.instance.handle_errors()
        self.assertEqual(self.instance.status, 204,
                         "Expected EdurepOAIPMH to translate noRecordsMatch error into a no content response")
