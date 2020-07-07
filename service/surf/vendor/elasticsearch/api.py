from collections import defaultdict

from django.conf import settings
from elasticsearch import Elasticsearch

from surf.apps.querylog.models import QueryLog
from surf.vendor.search.choices import DISCIPLINE_CUSTOM_THEME


_VCARD_FORMATED_NAME_KEY = "FN"


class ElasticSearchApiClient:

    def __init__(self, elastic_url=settings.ELASTICSEARCH_HOST, protocol=settings.ELASTICSEARCH_PROTOCOL):
        protocol_config = {} if protocol == "http" else {"scheme": "https", "port": 443}
        self.elastic = Elasticsearch(
            [elastic_url],
            http_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD),
            **protocol_config
        )
        self.index_nl = settings.ELASTICSEARCH_NL_INDEX
        self.index_en = settings.ELASTICSEARCH_EN_INDEX

    @staticmethod
    def parse_elastic_result(search_result):
        """
        Parses the elasticsearch search result into the format that is also used by the edurep endpoint.
        This allows quick switching between elastic and edurep without changing code.
        :param search_result: result from elasticsearch
        :return result: list of results in edurep format
        """
        hits = search_result["hits"]
        aggregations = search_result.get("aggregations", {})
        result = dict()
        result['recordcount'] = hits['total']

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
        record = dict()
        record['external_id'] = hit['_source']['external_id']
        record['url'] = hit['_source']['url']
        record['title'] = hit['_source']['title']
        record['description'] = hit['_source']['description']
        record['keywords'] = hit['_source']['keywords']
        record['language'] = hit['_source']['language']
        record['publish_datetime'] = hit['_source']['publisher_date']
        record['publishers'] = hit['_source']['publishers']
        record['authors'] = hit['_source']['authors']
        record['format'] = hit['_source']['file_type']
        record['disciplines'] = hit['_source']['disciplines']
        record['educationallevels'] = hit['_source'].get('lom_educational_levels', [])
        record['copyright'] = hit['_source']['copyright']
        themes = set()
        for discipline in hit['_source']['disciplines']:
            if discipline in DISCIPLINE_CUSTOM_THEME:
                themes.update(DISCIPLINE_CUSTOM_THEME[discipline])
        record['themes'] = list(themes)
        record['source'] = hit['_source']['arrangement_collection_name']
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
                        "field": "suggest"
                    }
                }
            }
        }

        result = self.elastic.search(
            index=[self.index_nl, self.index_en],
            doc_type='entity',
            body=query_dictionary,
            _source_include='suggest'
        )

        # extract the options from the elasticsearch result, remove duplicates,
        # remove non-matching prefixes (elastic will suggest things that don't match _exactly_)
        # and sort by length
        autocomplete = result['suggest']['autocomplete']
        options = autocomplete[0]['options']
        flat_options = list(set([item for option in options for item in option['_source']['suggest']]))
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

    def search(self, search_text: list, drilldown_names=None, filters=None, ordering=None, page=1, page_size=5):
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
        search_text = search_text or []
        assert isinstance(search_text, list), "A search needs to be specified as a list of terms"

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

        if len(search_text):
            query_string = {
                "query_string": {
                    "fields": ["title^2", "title_plain^2", "text", "text_plain", "description", "keywords", "authors"],
                    "query": ' AND '.join(search_text)
                }
            }
            body["query"]["bool"]["must"] += [query_string]

        indices = self.parse_index_language(self, filters)

        if drilldown_names:
            body["aggs"] = self.parse_aggregations(drilldown_names, filters)

        filters = self.parse_filters(filters)
        if filters:
            body["post_filter"]["bool"]["must"] += [filters]

        if ordering:
            body["sort"] = [
                self.parse_ordering(ordering),
                "_score"
            ]
        # make query and parse
        result = self.elastic.search(
            index=indices,
            body=body
        )
        parsed_result = self.parse_elastic_result(result)
        # store the searches in the database to be able to analyse them later on.
        # however, dont store results when scrolling as not to overload the database
        if start_record == 0 and search_text:
            url = f"es.search(index={indices}, body={body})"
            QueryLog(search_text=" AND ".join(search_text), filters=filters, query_url=url,
                     result_size=parsed_result['recordcount'], result=parsed_result).save()
        return parsed_result

    def get_materials_by_id(self, external_ids, **kwargs):
        """
        Retrieve specific materials from elastic through their external id.
        :param external_ids: the id's of the materials to retrieve
        :return: a list of search results (like a regular search).
        """
        result = self.elastic.search(
            index=[self.index_nl, self.index_en],
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
        indices = [self.index_nl, self.index_en]
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
            return 'file_type'
        elif external_id == 'about.repository':
            return 'arrangement_collection_name'  # TODO: should become oaipmh_set
        elif external_id == 'lom.rights.copyrightandotherrestrictions':
            return 'copyright.keyword'
        elif external_id == 'lom.classification.obk.educationallevel.id':
            return 'educational_levels'
        elif external_id == 'lom.educational.context':
            return 'lom_educational_levels'
        elif external_id == 'lom.lifecycle.contribute.publisherdate':
            return 'publisher_date'
        elif external_id == 'lom.classification.obk.discipline.id':
            return 'disciplines'
        elif external_id == 'lom.lifecycle.contribute.author':
            return 'authors'
        elif external_id == 'lom.general.language':
            return 'language.keyword'
        elif external_id == 'lom.general.aggregationlevel':
            return 'aggregation_level'
        elif external_id == 'lom.lifecycle.contribute.publisher':
            return 'publishers'
        return external_id
