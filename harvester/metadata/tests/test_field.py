from unittest.mock import patch, MagicMock

from django.test import TestCase

from metadata.models import MetadataField


search_client_mock = MagicMock()
search_client_mock.search = MagicMock(return_value={
    "aggregations": {
        "field1": {
            "buckets": [
                {
                    "key": "value1",
                    "doc_count": 1
                },
                {
                    "key": "value2",
                    "doc_count": 2
                },
                {
                    "key": "value3",
                    "doc_count": 3
                }
            ]
        }
    }
})


class TestMetadataFieldManager(TestCase):

    @patch("metadata.models.field.get_opensearch_client", return_value=search_client_mock)
    def test_fetch_value_frequencies(self, client_mock):
        frequencies = MetadataField.objects.fetch_value_frequencies()
        # Check dummy return values
        self.assertEqual(client_mock.call_count, 1)
        self.assertEqual(frequencies, {"field1": {"value1": 1, "value2": 2, "value3": 3}})
        # See if call to ES was made correctly
        args, kwargs = search_client_mock.search.call_args
        self.assertEqual(kwargs["index"], ["latest-nl", "latest-en", "latest-unk"])
        fields = kwargs["body"]["aggs"]
        for field in MetadataField.objects.all():
            self.assertIn(field.name, fields)
            self.assertEqual(fields[field.name]["terms"]["size"], field.metadatavalue_set.count() + 500)
