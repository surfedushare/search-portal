from django.test import SimpleTestCase
from unittest.mock import Mock
from django.core.exceptions import PermissionDenied

from surf.apps.core import RestrictAdminAccess


class TestsMiddleware(SimpleTestCase):

    def setUp(self):
        self.middleware = RestrictAdminAccess(Mock())
        self.request = Mock()

    def test_admin_access_outside_range(self):
        self.request.META = {
            "REMOTE_ADDR": "18.15.2.234"
        }
        self.request.path = '/admin/'
        with self.settings(ADMIN_IP_WHITELIST=["194.171.28.0/27"]):
            with self.assertRaises(PermissionDenied):
                self.middleware(self.request)

    def test_non_admin_access_outside_range(self):
        self.request.META = {
            "REMOTE_ADDR": "18.15.2.234"
        }
        self.request.path = '/'
        with self.settings(ADMIN_IP_WHITELIST=["194.171.28.0/27"]):
            try:
                self.middleware(self.request)
            except PermissionDenied:
                self.fail("Permission should be granted")

    def test_admin_access_inside_range(self):
        self.request.META = {
            "REMOTE_ADDR": "18.15.2.234"
        }
        self.request.path = '/admin/'
        with self.settings(ADMIN_IP_WHITELIST=["0.0.0.0/0"]):
            try:
                self.middleware(self.request)
            except PermissionDenied:
                self.fail("Permission should be granted")

    def test_admin_access_with_multiple_ranges(self):
        self.request.META = {
            "REMOTE_ADDR": "18.15.2.234"
        }
        self.request.path = '/admin/'
        with self.settings(ADMIN_IP_WHITELIST=["193.171.28.0/27", "18.15.2.234/32"]):
            try:
                self.middleware(self.request)
            except PermissionDenied:
                self.fail("Permission should be granted")

    def test_admin_access_included_in_x_http_forwarded_for(self):
        self.request.META = {
            "HTTP_X_FORWARDED_FOR": "127.0.0.1, 18.15.2.234"
        }
        self.request.path = '/admin/'
        with self.settings(ADMIN_IP_WHITELIST=["193.171.28.0/27", "18.15.2.234/32"]):
            try:
                self.middleware(self.request)
            except PermissionDenied:
                self.fail("Permission should be granted")

    def test_admin_access_not_included_in_x_http_forwarded_for(self):
        self.request.META = {
            "HTTP_X_FORWARDED_FOR": "127.0.0.1, 18.15.2.234"
        }
        self.request.path = '/admin/'
        with self.settings(ADMIN_IP_WHITELIST=["194.171.28.0/27"]):
            with self.assertRaises(PermissionDenied):
                self.middleware(self.request)
