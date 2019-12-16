from collections import defaultdict

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

        hits = search_result["hits"]
        aggregations = search_result.get("aggregations", {})
        result = dict()
        result['recordcount'] = hits['total']

        # Transform aggregations into drilldowns
        drilldowns = []
        for aggregation_name, aggregation in aggregations.items():
            items = [
                {
                    "external_id": bucket["key"],
                    "count": bucket["doc_count"]
                }
                for bucket in aggregation["buckets"]
            ]
            drilldowns.append({
                "external_id": aggregation_name,
                "items": items
            })
        result['drilldowns'] = drilldowns

        # Transform hits into records
        result['records'] = []
        for material in hits['hits']:
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
            new_material['source'] = material['_source']['arrangement_collection_name']
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
        search_results = self.search(search_text=search_text, filters=filters, drilldown_names=drilldown_names)
        search_results["records"] = []
        return search_results

    def search(self, search_text: list, drilldown_names=None, filters=None, ordering=None, page=1, page_size=5):
        search_text = search_text or []
        assert isinstance(search_text, list), "A search needs to be specified as a list of terms"
        # build basic query
        start_record = page_size * (page - 1) + 1
        body = {
            'query': {
                "bool": defaultdict(list)
            },
            'from': start_record,
            'size': page_size,
        }
        # add a search query if any
        if len(search_text):
            query_string = {
                "query_string": {
                    "fields": ["text", "title"],
                    "query": ' AND '.join(search_text)
                }
            }
            body["query"]["bool"]["must"] += [query_string]
        # apply filters
        filters = self.parse_filters(filters)
        if filters:
            body["query"]["bool"]["must"] += filters
        # add aggregations
        if drilldown_names:
            body["aggs"] = self.parse_aggregations(drilldown_names)
        # add ordering
        if ordering:
            body["sort"] = [
                self.parse_ordering(ordering),
                "_score"
            ]
        # make query and parse
        result = self.elastic.search(
            index=[index_nl, index_en],
            body=body
        )
        return self.parse_elastic_result(result)

    def get_materials_by_id(self, external_ids):
        result = self.elastic.search(
            index=[index_nl, index_en],
            body={
                "query": {
                    "bool": {
                        "must": [{"terms": {"external_id": external_ids}}]
                    }
                },
            },
        )
        materials = self.parse_elastic_result(result)
        return materials

    @staticmethod
    def parse_filters(filters):
        filter_items = []
        if not filters:
            return {}
        date_filter = None
        for filter_item in filters:
            if not filter_item['items']:
                continue
            elastic_type = ElasticSearchApiClient.translate_external_id_to_elastic_type(filter_item['external_id'])
            if elastic_type == "publisher_date":
                date_filter = filter_item
                continue
            filter_items.append({
                "terms": {
                    elastic_type: filter_item["items"]
                }
            })
        if date_filter:
            lower_bound, upper_bound = date_filter["items"]
            filter_items.append({
                "range": {
                    "publisher_date": {
                        "gte": lower_bound,
                        "lte": upper_bound
                    }
                }
            })
        return filter_items

    @staticmethod
    def parse_aggregations(aggregation_names):
        aggregation_items = {}
        for aggregation_name in aggregation_names:
            elastic_type = ElasticSearchApiClient.translate_external_id_to_elastic_type(aggregation_name)
            aggregation_items[aggregation_name] = {
                "terms": {
                    "field": elastic_type
                }
            }
        return aggregation_items

    @staticmethod
    def parse_ordering(ordering):
        order = "asc"
        if ordering.startswith("-"):
            order = "desc"
            ordering = ordering[1:]
        elastic_type = ElasticSearchApiClient.translate_external_id_to_elastic_type(ordering)
        return {elastic_type: {"order": order}}

    @staticmethod
    def translate_external_id_to_elastic_type(external_id):
        if external_id == 'lom.technical.format':
            return 'file_type'
        elif external_id == 'about.repository':
            return 'arrangement_collection_name'
        elif external_id == 'lom.rights.copyrightandotherrestrictions':
            return 'copyright.keyword'
        elif external_id == 'lom.classification.obk.educationallevel.id':
            return 'educational_levels'
        elif external_id == "lom.lifecycle.contribute.publisherdate":
            return 'publisher_date'
        return external_id
