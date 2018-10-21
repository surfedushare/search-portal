import requests

from datetime import datetime

from urllib.parse import quote_plus

import logging

from surf.vendor.edurep.xml_endpoint.v1_2.xml_parser import parse_response

logger = logging.getLogger()

_API_ENDPOINT = "http://wszoeken.edurep.kennisnet.nl:8000"
_AUTOCOMPLETE_ENDPOINT = "{}/autocomplete".format(_API_ENDPOINT)
_LOM_SRU_ENDPOINT = "{}/edurep/sruns".format(_API_ENDPOINT)

_DATE_TYPE_FIELDS = set("lom.lifecycle.contribute.publisherdate")

_DATE_FORMAT = "%Y-%m-%d"

_BASE_QUERY = "edurep"
_API_VERSION = "1.2"
_OPERATION = "searchRetrieve"
_RECORD_PACKING = "xml"


class XmlEndpointApiClient:

    def autocomplete(self, prefix):
        url = "{}?prefix={}".format(_AUTOCOMPLETE_ENDPOINT, prefix)
        response = requests.get(url)
        return response.json()[1]

    def drilldowns(self, drilldown_names, query=None, filters=None):
        return self._call(query=query, filters=filters,
                          drilldown_names=drilldown_names)

    def search(self, query, drilldown_names=None, filters=None,
               sort_keys=None, page=1, page_size=5):
        return self._call(query=query, filters=filters,
                          drilldown_names=drilldown_names,
                          sort_keys=sort_keys,
                          startRecord=page,
                          maximumRecords=page_size)

    @staticmethod
    def _call(query=None, filters=None, drilldown_names=None,
              startRecord=1, maximumRecords=0, sort_keys=None,
              version="1.2", operation="searchRetrieve"):

        if not query:
            query = _BASE_QUERY
        else:
            query = '{} AND ("{}")'.format(_BASE_QUERY, query)

        filters = _filter_dict_to_cql(filters)
        if filters:
            query = "{} AND {}".format(query, filters)

        parameters = dict(version=version,
                          operation=operation,
                          recordPacking=_RECORD_PACKING,
                          query=quote_plus(query),
                          startRecord=startRecord,
                          maximumRecords=maximumRecords)

        if drilldown_names and isinstance(drilldown_names, list):
            parameters["x-term-drilldown"] = ",".join(drilldown_names)

        if sort_keys and isinstance(sort_keys, list):
            sort_keys = sort_keys[0]
            if sort_keys.startswith("-"):
                sort_keys = "{},,1".format("".join(sort_keys[1::]))
            else:
                sort_keys = "{},,0".format(sort_keys)
            parameters["sortKeys"] = sort_keys

        parameters = "&".join(["{}={}".format(k, v)
                               for k, v in parameters.items()])

        url = "{}?{}".format(_LOM_SRU_ENDPOINT, parameters)
        return parse_response(requests.get(url).text)


def _filter_dict_to_cql(filters):
    if not filters or not isinstance(filters, dict):
        return None

    filters_cqls = [_filter_to_cql(f, v) for f, v in filters.items()]
    return " AND ".join(["({})".format(f) for f in filters_cqls if f])


def _filter_to_cql(field_id, values):
    if not values or not isinstance(values, list):
        return None

    if field_id in _DATE_TYPE_FIELDS:
        return _date_filter_to_cql(field_id, values)
    else:
        return _list_filter_to_cql(field_id, values)


def _date_filter_to_cql(field_id, date_range):
    if len(date_range) != 2:
        return None

    date_from, date_to = [int(datetime.strptime(d, _DATE_FORMAT).timestamp())
                          if d else 0 for d in date_range]
    conditions = []
    if date_from:
        conditions.append('({} >= "{}")'.format(field_id, date_from))
    if date_to:
        conditions.append('({} <= "{}")'.format(field_id, date_to))
    return " AND ".join(conditions)


def _list_filter_to_cql(field_id, values):
    return " OR ".join(['{} exact "{}"'.format(field_id, v)
                        for v in values])
