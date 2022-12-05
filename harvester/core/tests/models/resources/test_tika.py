from unittest.mock import patch, MagicMock
import json 

from django.test import TestCase

from core.models import HttpTikaResource

class TestTikaResource(TestCase):

    def test_handle_error_with_exception(self):
        # for analyzing and optimization purposes we NOW set the status of the resource to 1 (failed)
        # in the future we should finetune this for specific use cases
        expected_data = [
            {
                "http-connection:target-ip-address": "145.97.38.100",
                "http-header:status-code": "200",
                "X-TIKA:Parsed-By-Full-Set": [
                    "org.apache.tika.parser.DefaultParser",
                    "org.apache.tika.parser.pkg.PackageParser",
                    "org.apache.tika.parser.mp4.MP4Parser",
                    "org.apache.tika.parser.EmptyParser"
                ],
                "X-TIKA:content_handler": "ToXMLContentHandler",
                "resourceName": "/file/dcb11873-2a88-4b8b-a771-c26e95f46b60",
                "http-connection:num-redirects": "1",
                "http-connection:target-url": "https://resources.wikiwijs.nl/file/dcb11873-2a88-4b8b-a771-c26e95f46b60",
                "X-TIKA:Parsed-By": [
                    "org.apache.tika.parser.DefaultParser",
                    "org.apache.tika.parser.pkg.PackageParser"
                ],
                "X-TIKA:parse_time_millis": "181",
                "X-TIKA:embedded_depth": "0",
                "X-TIKA:EXCEPTION:warn": "Something went wrong",                
                "Content-Length": "0",
                "http-header:content-type": "application/zip",
                "Content-Type": "application/zip"
            },
        ]
        expected_content_type = "application/json"
        resource = HttpTikaResource(status=200, head={ "content-type": expected_content_type }, body=json.dumps(expected_data))
        resource.handle_errors()
        self.assertEqual(resource.status, 1)

    def test_handle_error_with_no_content(self):
        # for analyzing and optimization purposes we NOW set the status of the resource to 1 (failed)
        # in the future we should finetune this for specific use cases
        expected_data = [
            {
                "http-connection:target-ip-address": "151.101.38.217",
                "http-header:status-code": "200",
                "X-TIKA:Parsed-By-Full-Set": [
                    "org.apache.tika.parser.DefaultParser",
                    "org.apache.tika.parser.html.HtmlParser"
                ],
                "X-TIKA:content_handler": "ToTextContentHandler",
                "resourceName": "apache-tika-14029765778009660889.tmp",
                "http-connection:num-redirects": "0",
                "http-connection:target-url": "https://www.webpagetest.org/blank.html",
                "X-TIKA:Parsed-By": [
                    "org.apache.tika.parser.DefaultParser",
                    "org.apache.tika.parser.html.HtmlParser"
                ],
                "dc:title": "Blank",
                "Content-Encoding": "windows-1252",
                "X-TIKA:parse_time_millis": "165",
                "X-TIKA:embedded_depth": "0",
                "X-TIKA:content": "",
                "Content-Length": "129",
                "http-header:content-type": "text/html",
                "Content-Type": "text/html; charset=windows-1252"
            }
        ]
        expected_content_type = "application/json"
        resource = HttpTikaResource(status=200, head={ "content-type": expected_content_type }, body=json.dumps(expected_data))
        resource.handle_errors()
        self.assertEqual(resource.status, 1)        