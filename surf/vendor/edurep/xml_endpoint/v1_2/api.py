import requests

from datetime import datetime

from urllib.parse import quote_plus

import logging

from surf.vendor.edurep.xml_endpoint.v1_2.xml_parser import parse_response
from surf.vendor.edurep.xml_endpoint.v1_2.choices import TECH_FORMAT_MIME_TYPES

logger = logging.getLogger()

TECH_FORMAT_FIELD_ID = "lom.technical.format"
AUTHOR_FIELD_ID = "lom.lifecycle.contribute.author"
PUBLISHER_DATE_FILED_ID = "lom.lifecycle.contribute.publisherdate"

_API_ENDPOINT = "http://wszoeken.edurep.kennisnet.nl:8000"
_AUTOCOMPLETE_ENDPOINT = "{}/autocomplete".format(_API_ENDPOINT)
_LOM_SRU_ENDPOINT = "{}/edurep/sruns".format(_API_ENDPOINT)

_DATE_TYPE_FIELDS = set(PUBLISHER_DATE_FILED_ID)

_DATE_FORMAT = "%Y-%m-%d"

_BASE_QUERY = "edurep"
_API_VERSION = "1.2"
_OPERATION = "searchRetrieve"
_RECORD_PACKING = "xml"
_EXTRA_RECORD_SCHEMA = "smbAggregatedData"


class XmlEndpointApiClient:

    def autocomplete(self, query):
        url = "{}?prefix={}".format(_AUTOCOMPLETE_ENDPOINT, query)
        response = requests.get(url)
        return response.json()[1]

    def drilldowns(self, drilldown_names, search_text=None, filters=None):
        return self._call(search_text=search_text, filters=filters,
                          drilldown_names=drilldown_names)

    def search(self, search_text, drilldown_names=None, filters=None,
               ordering=None, page=1, page_size=5):
        return self._call(search_text=search_text, filters=filters,
                          drilldown_names=drilldown_names,
                          ordering=ordering,
                          startRecord=page,
                          maximumRecords=page_size)

    @staticmethod
    def _call(search_text=None, filters=None, drilldown_names=None,
              startRecord=1, maximumRecords=0, ordering=None,
              version="1.2", operation="searchRetrieve"):

        if not search_text:
            query = _BASE_QUERY
        else:
            query = " AND ".join('("{}")'.format(q) for q in search_text)
            query = '{} AND {}'.format(_BASE_QUERY, query)

        filters = _filter_list_to_cql(filters)
        if filters:
            query = "{} AND {}".format(query, filters)

        parameters = dict(version=version,
                          operation=operation,
                          recordPacking=_RECORD_PACKING,
                          query=quote_plus(query),
                          startRecord=startRecord,
                          maximumRecords=maximumRecords)
        parameters["x-recordSchema"] = _EXTRA_RECORD_SCHEMA

        if drilldown_names and isinstance(drilldown_names, list):
            parameters["x-term-drilldown"] = ",".join(drilldown_names)

        if ordering and isinstance(ordering, list):
            sort_keys = ordering[0]
            if sort_keys.startswith("-"):
                sort_keys = "{},,1".format("".join(sort_keys[1::]))
            else:
                sort_keys = "{},,0".format(sort_keys)
            parameters["sortKeys"] = sort_keys

        parameters = "&".join(["{}={}".format(k, v)
                               for k, v in parameters.items()])

        url = "{}?{}".format(_LOM_SRU_ENDPOINT, parameters)
        return parse_response(requests.get(url).text)


def _filter_list_to_cql(filters):
    if not filters or not isinstance(filters, list):
        return None

    filters_cqls = [_filter_to_cql(f["id"], f["items"]) for f in filters]
    return " AND ".join(["({})".format(f) for f in filters_cqls if f])


def _filter_to_cql(field_id, values):
    if not values or not isinstance(values, list):
        return None

    if field_id in _DATE_TYPE_FIELDS:
        return _date_filter_to_cql(field_id, values)

    elif field_id == TECH_FORMAT_FIELD_ID:
        return _tech_format_filter_to_cql(field_id, values)

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


def _tech_format_filter_to_cql(field_id, values):
    m_types = list()
    for v in values:
        m_types_cqls = ['{} exact "{}"'.format(field_id, vi)
                        for vi in TECH_FORMAT_MIME_TYPES.get(v, [])]
        m_types.append(" OR ".join(m_types_cqls))
    return " OR ".join(m_types)
