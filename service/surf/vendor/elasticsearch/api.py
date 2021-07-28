import boto3
from collections import defaultdict
import sentry_sdk

from django.conf import settings
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

from surf.vendor.elasticsearch.serializers import SearchResultSerializer


class ElasticSearchApiClient:

    def __init__(self, elastic_url=settings.ELASTICSEARCH_HOST):

        protocol = settings.ELASTICSEARCH_PROTOCOL
        protocol_config = {}
        if protocol == "https":
            protocol_config = {
                "scheme": "https",
                "port": 443,
                "use_ssl": True,
                "verify_certs": settings.ELASTICSEARCH_VERIFY_CERTS,
            }

        if settings.IS_AWS:
            credentials = boto3.Session().get_credentials()
            http_auth = AWS4Auth(credentials.access_key, credentials.secret_key, "eu-central-1", "es",
                                 session_token=credentials.token)
        else:
            http_auth = (None, None)

        self.client = Elasticsearch(
            [elastic_url],
            http_auth=http_auth,
            connection_class=RequestsHttpConnection,
            **protocol_config
        )
        self.index_nl = settings.ELASTICSEARCH_NL_INDEX
        self.index_en = settings.ELASTICSEARCH_EN_INDEX
        self.index_unk = settings.ELASTICSEARCH_UNK_INDEX

    @staticmethod
    def parse_elastic_result(search_result):
        """
        Parses the elasticsearch search result into the format that is also used by the edurep endpoint.
        This allows quick switching between elastic and edurep without changing code.
        :param search_result: result from elasticsearch
        :return result: list of results in edurep format
        """
        hits = search_result.pop("hits")
        aggregations = search_result.get("aggregations", {})
        result = dict()
        result['recordcount'] = hits['total']['value']

        # Transform aggregations into drilldowns
        drilldowns = []
        for aggregation_name, aggregation in aggregations.items():
            buckets = aggregation["filtered"]["buckets"] if "filtered" in aggregation else aggregation["buckets"]

            items = [
                {
                    "external_id": bucket["key"],
                    "count": bucket["doc_count"]
                }
                for bucket in buckets
            ]

            drilldowns.append({
                "external_id": aggregation_name,
                "items": items
            })

        result['drilldowns'] = drilldowns

        # Parse spelling suggestions
        did_you_mean = {}
        if 'suggest' in search_result:
            spelling_suggestion = search_result['suggest']['did-you-mean-suggestion'][0]
            spelling_option = spelling_suggestion['options'][0] if len(spelling_suggestion['options']) else None
            if spelling_option is not None and spelling_option["score"] >= 0.01:
                did_you_mean = {
                    'original': spelling_suggestion['text'],
                    'suggestion': spelling_option['text']
                }
        result['did_you_mean'] = did_you_mean

        # Transform hits into records
        result['records'] = [
            ElasticSearchApiClient.parse_elastic_hit(hit)
            for hit in hits['hits']
        ]
        return result

    @staticmethod
    def parse_elastic_hit(hit):
        """
        Parses the elasticsearch search hit into the format that is also used by the edurep endpoint.
        It's mostly just mapping the variables we need into the places that we expect them to be.
        :param hit: result from elasticsearch
        :return record: parsed record in elasticsearch format
        """
        field_mapping = {
            field.source: field_name
            for field_name, field in SearchResultSerializer().fields.items()
        }
        record = {
            field_mapping[field]: value
            for field, value in hit["_source"].items() if field in field_mapping
        }
        return record

    def autocomplete(self, query):
        """
        Use the elasticsearch suggest query to get typing hints during searching.
        :param query: the input from the user so far
        :return: a list of options matching the input query, sorted by length
        """
        # build the query for elasticsearch.
        query_dictionary = {
            'suggest': {
                "autocomplete": {
                    'text': query,
                    "completion": {
                        "field": "suggest_completion"
                    }
                }
            }
        }

        result = self.client.search(
            index=[self.index_nl, self.index_en, self.index_unk],
            body=query_dictionary
        )

        # extract the options from the elasticsearch result, remove duplicates,
        # remove non-matching prefixes (elastic will suggest things that don't match _exactly_)
        # and sort by length
        autocomplete = result['suggest']['autocomplete']
        options = autocomplete[0]['options']
        flat_options = list(set([item for option in options for item in option['_source']['suggest_completion']]))
        options_with_prefix = [option for option in flat_options if option.startswith(query)]
        options_with_prefix.sort(key=lambda option: len(option))
        return options_with_prefix

    def drilldowns(self, drilldown_names, search_text=None, filters=None):
        """
        This function is named drilldowns is because it's also named drilldowns in the original edurep search code.
        It passes on information to search, and returns the search without the records.
        This allows calculation of 'item counts' (i.e. how many results there are in through a certain filter)
        """
        search_results = self.search(search_text=search_text, filters=filters, drilldown_names=drilldown_names)
        search_results["records"] = []
        return search_results

    def search(self, search_text, drilldown_names=None, filters=None, ordering=None, page=1, page_size=5):
        """
        Build and send a query to elasticsearch and parse it before returning.
        :param search_text: A list of strings to search for.
        :param drilldown_names: A list of the 'drilldowns' (filters) that are to be counted by elasticsearch.
        :param filters: The filters that are applied for this search.
        :param ordering: Sort the results by this ordering (or use default elastic ordering otherwise)
        :param page: The page index of the results
        :param page_size: How many items are loaded per page.
        :return:
        """

        start_record = page_size * (page - 1)
        body = {
            'query': {
                "bool": defaultdict(list)
            },
            'from': start_record,
            'size': page_size,
            'post_filter': {
                "bool": defaultdict(list)
            }
        }

        if search_text:
            query_string = {
                "simple_query_string": {
                    "fields": [
                        "title^2", "title.analyzed^2", "title.folded^2",
                        "text", "text.analyzed", "text.folded",
                        "description", "description.analyzed", "description.folded",
                        "keywords", "keywords.folded",
                        "authors", "authors.folded",
                        "publishers", "publishers.folded",
                        "ideas", "ideas.folded"
                    ],
                    "query": search_text,
                    "default_operator": "and"
                }
            }
            body["query"]["bool"]["must"] += [query_string]
            body["query"]["bool"]["should"] = {
                "distance_feature": {
                    "field": "publisher_date",
                    "pivot": "90d",
                    "origin": "now",
                    "boost": 1.15
                }
            }
            body["suggest"] = {
                'did-you-mean-suggestion': {
                    'text': search_text,
                    'phrase': {
                        'field': 'suggest_phrase',
                        'size': 1,
                        'gram_size': 3,
                        'direct_generator': [{
                            'field': 'suggest_phrase',
                            'suggest_mode': 'always'
                        }],
                    },
                }
            }

        indices = self.parse_index_language(self, filters)

        if drilldown_names:
            body["aggs"] = self.parse_aggregations(drilldown_names, filters)

        filters = self.parse_filters(filters)
        if filters:
            body["post_filter"]["bool"]["must"] += filters

        if ordering:
            body["sort"] = [
                self.parse_ordering(ordering),
                "_score"
            ]
        # make query and parse
        result = self.client.search(
            index=indices,
            body=body
        )
        return self.parse_elastic_result(result)

    def get_materials_by_id(self, external_ids, page=1, page_size=10, **kwargs):
        """
        Retrieve specific materials from elastic through their external id.
        :param external_ids: the id's of the materials to retrieve
        :param page: The page index of the results
        :param page_size: How many items are loaded per page.
        :return: a list of search results (like a regular search).
        """
        start_record = page_size * (page - 1)

        normalized_external_ids = []
        for external_id in external_ids:
            if not external_id.startswith("surf"):
                normalized_external_ids.append(external_id)
            else:
                external_id_parts = external_id.split(":")
                normalized_external_ids.append(external_id_parts[-1])

        result = self.client.search(
            index=[self.index_nl, self.index_en, self.index_unk],
            body={
                "query": {
                    "bool": {
                        "must": [{"terms": {"external_id": normalized_external_ids}}]
                    }
                },
                'from': start_record,
                'size': page_size,
            },
        )
        results = self.parse_elastic_result(result)
        materials = {
            material["external_id"]: material
            for material in results["records"]
        }
        records = []
        for external_id in normalized_external_ids:
            if external_id not in materials:
                if not settings.DEBUG:
                    sentry_sdk.capture_message(
                        f"Failed to find material with external_id: {external_id}",
                        "warning"
                    )
                continue
            records.append(materials[external_id])
        results["recordcount"] = len(records)
        results["records"] = records
        return results

    @staticmethod
    def parse_filters(filters):
        """
        Parse filters from the edurep format into the elastic query format.
        Not every filter is handled by elastic in the same way so it's a lot of manual parsing.
        :param filters: the list of filters to be parsed
        :return: the filters in the format for an elasticsearch query.
        """
        if not filters:
            return {}
        filter_items = []
        for filter_item in filters:
            # skip filter_items that are empty
            # and the language filter item (it's handled by telling elastic in what index to search).
            if not filter_item['items'] or 'lom.general.language' in filter_item['external_id']:
                continue
            elastic_type = ElasticSearchApiClient.translate_external_id_to_elastic_type(filter_item['external_id'])
            # date range query
            if elastic_type == "publisher_date":
                lower_bound, upper_bound = filter_item["items"]
                if lower_bound is not None or upper_bound is not None:
                    filter_items.append({
                        "range": {
                            "publisher_date": {
                                "gte": lower_bound,
                                "lte": upper_bound
                            }
                        }
                    })
            # all other filter types are handled by just using elastic terms with the 'translated' filter items
            else:
                filter_items.append({
                    "terms": {
                        elastic_type: filter_item["items"]
                    }
                })
        return filter_items

    def parse_aggregations(self, aggregation_names, filters):
        """
        Parse the aggregations so elastic can count the items properly.
        :param aggregation_names: the names of the aggregations to
        :param filters: the filters for the query
        :return:
        """

        aggregation_items = {}
        for aggregation_name in aggregation_names:
            other_filters = []

            if filters:
                other_filters = list(filter(lambda x: x['external_id'] != aggregation_name, filters))
                other_filters = self.parse_filters(other_filters)

            elastic_type = ElasticSearchApiClient.translate_external_id_to_elastic_type(aggregation_name)

            if len(other_filters) > 0:
                # Filter the aggregation by the filters applied to other categories
                aggregation_items[aggregation_name] = {
                    "filter": {
                        "bool": {
                            "must": other_filters
                        }
                    },
                    "aggs": {
                        "filtered": {
                            "terms": {
                                "field": elastic_type,
                                "size": 500,
                            }
                        }
                    },
                }
            else:
                aggregation_items[aggregation_name] = {
                    "terms": {
                        "field": elastic_type,
                        "size": 500,
                    }
                }
        return aggregation_items

    @staticmethod
    def parse_ordering(ordering):
        """
        Parse the ordering format ('asc', 'desc' or None) into the type that elasticsearch expects.
        """
        order = "asc"
        if ordering.startswith("-"):
            order = "desc"
            ordering = ordering[1:]
        elastic_type = ElasticSearchApiClient.translate_external_id_to_elastic_type(ordering)
        return {elastic_type: {"order": order}}

    @staticmethod
    def parse_index_language(self, filters):
        """
        Select the index to search on based on language.
        """
        # if no language is selected, search on both.
        indices = [self.index_nl, self.index_en, self.index_unk]
        if not filters:
            return indices
        language_item = [filter_item for filter_item in filters if filter_item['external_id'] == 'lom.general.language']
        if not language_item:
            return indices
        language_indices = [f"latest-{language}" for language in language_item[0]['items']]
        return language_indices if len(language_indices) else indices

    @staticmethod
    def translate_external_id_to_elastic_type(external_id):
        """ The external id's used in edurep need to be parsed to fields in elasticsearch. """
        if external_id == 'lom.technical.format':
            return 'technical_type'
        elif external_id == 'about.repository':
            return 'harvest_source'
        elif external_id == 'lom.rights.copyrightandotherrestrictions':
            return 'copyright.keyword'
        elif external_id == 'lom.educational.context':
            return 'lom_educational_levels'
        elif external_id == 'lom.lifecycle.contribute.publisherdate':
            return 'publisher_date'
        elif external_id == 'lom.classification.obk.discipline.id':
            return 'disciplines'
        elif external_id == 'lom.lifecycle.contribute.author':
            return 'authors.keyword'
        elif external_id == 'lom.general.language':
            return 'language.keyword'
        elif external_id == 'lom.general.aggregationlevel':
            return 'aggregation_level'
        elif external_id == 'lom.lifecycle.contribute.publisher':
            return 'publishers.keyword'
        return external_id
