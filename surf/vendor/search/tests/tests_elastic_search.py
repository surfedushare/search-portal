from surf.vendor.elasticsearch.api import ElasticSearchApiClient
from .base import get_base_search_test_class


class ElasticSearchTestCase(get_base_search_test_class()):
    test_class = ElasticSearchApiClient

    def test_search_by_author(self):
        author = "John van Dongen"
        expected_record_count = 2
        self.check_author_search(author, expected_record_count)

        author2 = "Ruud Kok"
        expected_record_count2 = 3
        self.check_author_search(author2, expected_record_count2)

    def check_author_search(self, author, expected_record_count):
        search_author = self.instance.search(
            [],
            filters=[{"external_id": "lom.lifecycle.contribute.author", "items": [author]}]
        )
        for record in search_author['records']:
            self.assertEqual(record['author'], author)
        self.assertEqual(search_author['recordcount'], expected_record_count)

