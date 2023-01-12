from collections import defaultdict

from django.conf import settings
from opensearchpy import OpenSearch, RequestsHttpConnection

from project.configuration import SEARCH_FIELDS
from surf.vendor.search.serializers import SearchResultSerializer


class SearchApiClient:

    def __init__(self, host=settings.OPENSEARCH_HOST):

        protocol = settings.OPENSEARCH_PROTOCOL
        protocol_config = {}
        if protocol == "https":
            protocol_config = {
                "scheme": "https",
                "port": 443,
                "use_ssl": True,
                "verify_certs": settings.OPENSEARCH_VERIFY_CERTS,
            }

        if settings.IS_AWS:
            http_auth = ("supersurf", settings.OPENSEARCH_PASSWORD)
        else:
            http_auth = (None, None)

        self.client = OpenSearch(
            [host],
            http_auth=http_auth,
            connection_class=RequestsHttpConnection,
            **protocol_config
        )
        self.index_nl = settings.OPENSEARCH_NL_INDEX
        self.index_en = settings.OPENSEARCH_EN_INDEX
        self.index_unk = settings.OPENSEARCH_UNK_INDEX
        self.languages = {
            "nl": self.index_nl,
            "en": self.index_en
        }

    @staticmethod
    def parse_search_result(search_result):
        """
        Parses the search result into the correct format that the frontend uses

        :param search_result: result from search
        :return result: list of results ready for frontend
        """
        hits = search_result.pop("hits")
        aggregations = search_result.get("aggregations", {})
        result = dict()
        result['recordcount'] = hits['total']['value']

        # Transform aggregations into drilldowns
        drilldowns = {}
        for aggregation_name, aggregation in aggregations.items():
            buckets = aggregation["filtered"]["buckets"] if "filtered" in aggregation else aggregation["buckets"]
            for bucket in buckets:
                drilldowns[f"{aggregation_name}-{bucket['key']}"] = bucket["doc_count"]
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
            SearchApiClient.parse_search_hit(hit)
            for hit in hits['hits']
        ]
        return result

    @staticmethod
    def parse_search_hit(hit, transform=True):
        """
        Parses the search hit into the format that is also used by the edurep endpoint.
        It's mostly just mapping the variables we need into the places that we expect them to be.
        :param hit: result from search
        :return record: parsed record
        """
        data = hit["_source"]
        serializer = SearchResultSerializer()
        # Basic mapping between field and data (excluding any method fields with a source of "*")
        field_mapping = {
            field.source: field_name if transform else field.source
            for field_name, field in serializer.fields.items() if field.source != "*"
        }
        record = {
            field_mapping[field]: value
            for field, value in data.items() if field in field_mapping
        }
        # Reformatting some fields if a relations field is desired
        if "relations" in field_mapping:
            publishers = [{"name": publisher} for publisher in data.get("publishers", [])]
            keywords = data.get("keywords", []) or []
            record["relations"] = {
                "authors": data.get("authors", []),
                "parties": data.get("parties", []) or publishers,
                "projects": data.get("projects", []),
                "keywords": [{"label": keyword} for keyword in keywords],
                "themes": [{"label": theme} for theme in data.get("research_themes", [])],
                "parents": data.get("is_part_of", []),
                "children": data.get("has_parts", [])
            }
        # Calling methods on serializers to set data for method fields
        for field_name, field in serializer.fields.items():
            if field.source != "*":
                continue
            record[field_name] = getattr(serializer, field.method_name)(data)

        # Add highlight to the record
        if hit.get("highlight", 0):
            record["highlight"] = hit["highlight"]

        return record

    def autocomplete(self, query):
        """
        Use the suggest query to get typing hints during searching.

        :param query: the input from the user so far
        :return: a list of options matching the input query, sorted by length
        """
        # build the query for search engine
        query_dictionary = {
            'suggest': {
                "autocomplete": {
                    'text': query,
                    "completion": {
                        "field": "suggest_completion",
                        "size": 100
                    }
                }
            }
        }

        result = self.client.search(
            index=[self.index_nl, self.index_en, self.index_unk],
            body=query_dictionary
        )

        # extract the options from the search result, remove duplicates,
        # remove non-matching prefixes (engine will suggest things that don't match _exactly_)
        # and sort by length
        autocomplete = result['suggest']['autocomplete']
        options = autocomplete[0]['options']
        flat_options = list(set([item for option in options for item in option['_source']['suggest_completion']]))
        options_with_prefix = [option for option in flat_options if option.lower().startswith(query.lower())]
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
        Build and send a query to search engine and parse it before returning.

        :param search_text: A list of strings to search for.
        :param drilldown_names: A list of the 'drilldowns' (filters) that are to be counted by engine.
        :param filters: The filters that are applied for this search.
        :param ordering: Sort the results by this ordering (or use default search ordering otherwise)
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
            },
            'highlight': {
                'number_of_fragments': 1,
                'fragment_size': 120,
                'fields': {
                    'description': {},
                    'text': {}
                }
            }
        }

        if search_text:
            query_string = {
                "simple_query_string": {
                    "fields": SEARCH_FIELDS,
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
        return self.parse_search_result(result)

    def get_materials_by_id(self, external_ids, page=1, page_size=10, **kwargs):
        """
        Retrieve specific materials from search engine through their external id.

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
        results = self.parse_search_result(result)
        materials = {
            material["external_id"]: material
            for material in results["records"]
        }
        records = []
        for external_id in normalized_external_ids:
            if external_id not in materials:
                continue
            records.append(materials[external_id])
        results["recordcount"] = len(records)
        results["records"] = records
        return results

    def stats(self):
        stats = self.client.count(index=",".join([self.index_nl, self.index_en, self.index_unk]))
        return stats.get("count", 0)

    def more_like_this(self, external_id, language):
        index = self.languages.get(language, self.index_unk)
        body = {
            "query": {
                "more_like_this": {
                    "fields": ["title", "description"],
                    "like": [
                        {
                            "_index": index,
                            "_id": external_id
                        }
                    ],
                    "min_term_freq": 1,
                    "max_query_terms": 12
                }
            }
        }
        search_result = self.client.search(
            index=index,
            body=body
        )
        hits = search_result.pop("hits")
        result = dict()
        result["records_total"] = hits["total"]["value"]
        result["results"] = [
            SearchApiClient.parse_search_hit(hit, transform=False)
            for hit in hits["hits"]
        ]
        return result

    def author_suggestions(self, author_name):
        body = {
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "fields": [field for field in SEARCH_FIELDS if "authors" not in field],
                            "query": author_name,
                        },
                    },
                    "must_not": {
                        "match": {"authors.name.folded": author_name}
                    }
                }
            }
        }
        search_result = self.client.search(
            index=[self.index_nl, self.index_en, self.index_unk],
            body=body
        )
        hits = search_result.pop("hits")
        result = dict()
        result["records_total"] = hits["total"]["value"]
        result["results"] = [
            SearchApiClient.parse_search_hit(hit, transform=False)
            for hit in hits["hits"]
        ]
        return result

    @staticmethod
    def parse_filters(filters):
        """
        Parse filters from the frontend format into the search engine format.
        Not every filter is handled by search engine  in the same way so it's a lot of manual parsing.

        :param filters: the list of filters to be parsed
        :return: the filters in the format for a search query.
        """
        if not filters:
            return {}
        filter_items = []
        for filter_item in filters:
            # skip filter_items that are empty
            # and the language filter item (it's handled by telling search engine in what index to search).
            if not filter_item['items'] or 'language.keyword' in filter_item['external_id']:
                continue
            search_type = filter_item['external_id']
            # date range query
            if search_type == "publisher_date":
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
            # all other filter types are handled by just using terms with the 'translated' filter items
            else:
                filter_items.append({
                    "terms": {
                        search_type: filter_item["items"]
                    }
                })
        return filter_items

    def parse_aggregations(self, aggregation_names, filters):
        """
        Parse the aggregations so search engine can count the items properly.

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

            search_type = aggregation_name

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
                                "field": search_type,
                                "size": 2000,
                            }
                        }
                    },
                }
            else:
                aggregation_items[aggregation_name] = {
                    "terms": {
                        "field": search_type,
                        "size": 2000,
                    }
                }
        return aggregation_items

    @staticmethod
    def parse_ordering(ordering):
        """
        Parse the frontend ordering format ('asc', 'desc' or None) into the type that search engine expects.
        """
        order = "asc"
        if ordering.startswith("-"):
            order = "desc"
            ordering = ordering[1:]
        search_type = ordering
        return {search_type: {"order": order}}

    @staticmethod
    def parse_index_language(self, filters):
        """
        Select the index to search on based on language.
        """
        # if no language is selected, search on both.
        indices = [self.index_nl, self.index_en, self.index_unk]
        if not filters:
            return indices
        language_item = [filter_item for filter_item in filters if filter_item['external_id'] == 'language.keyword']
        if not language_item:
            return indices
        language_indices = [f"{settings.SITE_SLUG}-{language}" for language in language_item[0]['items']]
        return language_indices if len(language_indices) else indices
