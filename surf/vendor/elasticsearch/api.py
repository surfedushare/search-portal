from django.conf import settings
from elasticsearch import Elasticsearch
from surf.vendor.edurep.xml_endpoint.v1_2.xml_parser import _parse_vcard

index_nl = 'latest-nl'
index_en = 'latest-en'
_VCARD_FORMATED_NAME_KEY = "FN"


class ElasticSearchApiClient:
    def __init__(self, elastic_url=settings.ELASTICSEARCH_URL):
        self.elastic = Elasticsearch(
            [elastic_url],
            http_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD),
            scheme="https",
            port=443,
        )

    @staticmethod
    def parse_elastic_result(search_result):
        material_keys = ['object_id', 'url', 'title', 'description', 'keywords', 'language', 'aggregationlevel',
                         'publisher', 'publish_datetime', 'author', 'format', 'educationallevels',
                         'themes', 'disciplines']

        result = dict()
        result['recordcount'] = search_result['hits']['total']
        # TODO
        result['drilldowns'] = []

        # TODO
        result['records'] = []
        for material in search_result['hits']['hits']:

            new_material = dict()
            new_material['external_id'] = material['_source']['external_id']
            new_material['url'] = material['_source']['url']
            new_material['title'] = material['_source']['title']
            new_material['description'] = material['_source']['description']
            new_material['keywords'] = material['_source']['keywords']
            new_material['language'] = material['_source']['language']
            new_material['publish_datetime'] = material['_source']['publisher_date']
            author = material['_source']['author']
            if author and isinstance(author, list):
                author = _parse_vcard(author[0]).get(_VCARD_FORMATED_NAME_KEY)
            if not author:
                author = None
            new_material['author'] = author
            new_material['format'] = material['_source']['file_type']
            new_material['disciplines'] = material['_source']['disciplines']
            new_material['educationallevels'] = material['_source']['educational_levels']
            new_material['copyright'] = material['_source']['copyright']
            new_material['themes'] = None  # TODO
            result['records'].append(new_material)
        return result

    def autocomplete(self, query):
        query_dictionary = {
            'suggest': {
                "autocomplete": {
                    'text': query,
                    "completion": {
                        "field": "suggest"
                    }
                }
            }
        }

        result = self.elastic.search(
            index=[index_nl, index_en],
            doc_type='entity',
            body=query_dictionary,
            _source_include='suggest'
        )

        autocomplete = result['suggest']['autocomplete']
        options = autocomplete[0]['options']
        flat_options = list(set([item for option in options for item in option['_source']['suggest']]))
        options_with_prefix = [option for option in flat_options if option.startswith(query)]
        options_with_prefix.sort(key=lambda option: len(option))
        return options_with_prefix

    def drilldowns(self, drilldown_names, search_text=None, filters=None):
        return self._search(search_text=search_text, filters=filters, drilldown_names=drilldown_names)

    def search(self, search_text: str, drilldown_names=None, filters=None, ordering=None, page=1, page_size=5):
        filters = self.parse_filters(filters)
        # searching in elastic with an empty string returns no hits
        if search_text == "":
            search_text = None
        start_record = page_size * (page - 1) + 1
        result = self.elastic.search(
            index=[index_nl, index_en],
            q=search_text,
            body={'from': start_record,
                  'size': page_size,
                  # 'query': {
                  #       ",".join([str(item) for item in filters])
                  #     }
                  }
        )

        return self.parse_elastic_result(result)

    def get_materials_by_id(self, external_ids, page=1, page_size=5, drilldown_names=None):
        start_record = page_size * (page - 1) + 1
        result = self.elastic.search(
            index=[index_nl, index_en],
            body={
                "query": {
                    "bool": {
                        "must": [{"terms": {"external_id": external_ids}}]
                    }
                },
                # "from": start_record,
                # "size": page_size
            },
        )
        materials = self.parse_elastic_result(result)
        return materials

    @staticmethod
    def parse_filters(filters):
        filter_items = []
        if filters:
            for filter_item in filters:
                if filter_item['items']:
                    elastic_type = filters.translate_external_id_to_elastic_type(filter_item['external_id'])
                    term = {"bool": {"must": [{"terms": {elastic_type: filter_item['items']}}]}}
                    filter_items.append(term)
        return filter_items

    @staticmethod
    def translate_external_id_to_elastic_type(external_id):
        if external_id == 'lom.technical.format':
            return 'file_type'
        return external_id


