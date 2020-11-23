"""
This module provides integration with JSON-based endpoint of EduRep API.
"""

import requests

from surf.vendor.edurep.xml_endpoint.v1_2.api import filter_list_to_cql

_DEFAULT_API_ENDPOINT = "https://proxy.edurep.nl/v3/search"

_BASE_QUERY = "edurep"


class WidgetEndpointApiClient:
    """
    Class provides integration with JSON-based endpoint of EduRep API
    """

    def __init__(self, api_endpoint=_DEFAULT_API_ENDPOINT):
        self.api_endpoint = api_endpoint

    def drilldowns(self, drilldown_names, query=None, filters=None):
        """
        Returns statistics with count of materials for each item of
        each drilldown name (filter category) for material searching query
        :param drilldown_names: list of drilldown names
        :param query: query to search materials
        :param filters: list of filters to search materials
        :return: list of drilldowns
        """

        if query:
            query = '{} AND ("{}")'.format(_BASE_QUERY, query)
        else:
            query = _BASE_QUERY

        filters = filter_list_to_cql(filters)
        if filters:
            # add to query CQL-expression related to filters
            query = "{} AND {}".format(query, filters)

        url = "{}?mode=json&query={}&maximumRecords=0&x-term-drilldown={}".format(
            self.api_endpoint,
            query,
            ",".join(drilldown_names))

        response = requests.get(url)

        if response and response.status_code != requests.codes.ok:
            response.raise_for_status()

        try:
            search = response.json()["search"]

            if not search:
                return dict()

            return search["drilldowns"]
        except KeyError:
            return dict()
