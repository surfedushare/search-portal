import requests

from datetime import datetime

from urllib.parse import quote_plus

import logging

from surf.vendor.edurep.xml_endpoint.v1_2.xml_parser import (
    parse_response,
    TECH_FORMAT_LOM,
    CUSTOM_THEME_ID,
    DISCIPLINE_ID_LOM,
    COPYRIGHT_ID_LOM
)

from surf.vendor.edurep.xml_endpoint.v1_2.choices import (
    TECH_FORMAT_MIME_TYPES,
    CUSTOM_THEME_DISCIPLINES,
    CUSTOM_COPYRIGHTS
)

logger = logging.getLogger()

TECH_FORMAT_FIELD_ID = TECH_FORMAT_LOM
CUSTOM_THEME_FIELD_ID = CUSTOM_THEME_ID
DISCIPLINE_FIELD_ID = DISCIPLINE_ID_LOM
COPYRIGHT_FIELD_ID = COPYRIGHT_ID_LOM
AUTHOR_FIELD_ID = "lom.lifecycle.contribute.author"
PUBLISHER_FIELD_ID = "lom.lifecycle.contribute.publisher"
PUBLISHER_DATE_FIELD_ID = "lom.lifecycle.contribute.publisherdate"
EDUCATIONAL_LEVEL_FIELD_ID = "lom.classification.obk.educationallevel.id"

_DEFAULT_API_ENDPOINT = "http://wszoeken.edurep.kennisnet.nl:8000"

_DATE_TYPE_FIELDS = {PUBLISHER_DATE_FIELD_ID}

_DATE_FORMAT = "%Y-%m-%d"
_EDUREP_DATE_FORMAT = "%Y%m%d"

_BASE_QUERY = "edurep"
_API_VERSION = "1.2"
_OPERATION = "searchRetrieve"
_RECORD_PACKING = "xml"
_EXTRA_RECORD_SCHEMA = "smbAggregatedData"


class XmlEndpointApiClient:

    def __init__(self, api_endpoint=_DEFAULT_API_ENDPOINT):
        self.api_endpoint = api_endpoint

    def autocomplete(self, query):
        url = "{}/autocomplete?prefix={}".format(self.api_endpoint, query)

        response = requests.get(url)
        if response and response.status_code != requests.codes.ok:
            response.raise_for_status()

        _, keywords = response.json()
        return keywords

    def drilldowns(self, drilldown_names, search_text=None, filters=None):
        return self._search(search_text=search_text, filters=filters,
                            drilldown_names=drilldown_names)

    def search(self, search_text, drilldown_names=None, filters=None,
               ordering=None, page=1, page_size=5):
        start_record = _get_start_record_by_page(page, page_size)
        return self._search(search_text=search_text, filters=filters,
                            drilldown_names=drilldown_names,
                            ordering=ordering,
                            start_record=start_record,
                            maximum_records=page_size)

    def get_materials_by_id(self, external_ids, page=1, page_size=5,
                            drilldown_names=None):
        start_record = _get_start_record_by_page(page, page_size)
        id_set = set(external_ids)
        rv = self._call(query=" OR ".join(external_ids),
                        start_record=start_record, maximum_records=page_size,
                        drilldown_names=drilldown_names)

        rv["records"] = [m for m in rv["records"]
                         if m["external_id"] in id_set or
                         '"{}"'.format(m["external_id"]) in id_set]
        return rv

    def _search(self, search_text=None, filters=None, drilldown_names=None,
                start_record=1, maximum_records=0, ordering=None):

        if search_text:
            query = " AND ".join('("{}")'.format(q) for q in search_text)
            query = '{} AND {}'.format(_BASE_QUERY, query)
        else:
            query = _BASE_QUERY

        filters = filter_list_to_cql(filters)
        if filters:
            query = "{} AND {}".format(query, filters)

        return self._call(query=query,
                          drilldown_names=drilldown_names,
                          ordering=ordering,
                          start_record=start_record,
                          maximum_records=maximum_records)

    def _call(self, query, drilldown_names=None,
              start_record=1, maximum_records=0, ordering=None,
              version="1.2", operation="searchRetrieve"):

        parameters = dict(version=version,
                          operation=operation,
                          recordPacking=_RECORD_PACKING,
                          query=quote_plus(query, safe=''),
                          startRecord=start_record,
                          maximumRecords=maximum_records)
        parameters["x-recordSchema"] = _EXTRA_RECORD_SCHEMA

        if drilldown_names and isinstance(drilldown_names, list):
            parameters["x-term-drilldown"] = ",".join(drilldown_names)

        if ordering:
            if isinstance(ordering, list):
                ordering = ordering[0]

            if ordering.startswith("-"):
                sort_keys = "{},,1".format("".join(ordering[1::]))
            else:
                sort_keys = "{},,0".format(ordering)
            parameters["sortKeys"] = sort_keys

        parameters = "&".join(["{}={}".format(k, v)
                               for k, v in parameters.items()])

        url = "{}/edurep/sruns?{}".format(self.api_endpoint, parameters)

        response = requests.get(url)
        if response and response.status_code != requests.codes.ok:
            response.raise_for_status()

        return parse_response(response.text)


def _get_start_record_by_page(page, page_size):
    return page_size * (page - 1) + 1


def filter_list_to_cql(filters):
    """
    Creates CQL string by list of filters
    :param filters: list of filters
    :return: query string in CQL
    """

    if not filters or not isinstance(filters, list):
        return None

    filters_cqls = [_filter_to_cql(f["external_id"], f["items"])
                    for f in filters]

    return " AND ".join(["({})".format(f) for f in filters_cqls if f])


def _filter_to_cql(field_id, values):
    if not values or not isinstance(values, list):
        return None

    if field_id in _DATE_TYPE_FIELDS:
        return _date_filter_to_cql(field_id, values)

    elif field_id == TECH_FORMAT_FIELD_ID:
        return _tech_format_filter_to_cql(field_id, values)

    elif field_id == CUSTOM_THEME_FIELD_ID:
        return _custom_theme_filter_to_cql(DISCIPLINE_ID_LOM, values)

    elif field_id == COPYRIGHT_FIELD_ID:
        vs = list()
        for v in values:
            vs.extend(CUSTOM_COPYRIGHTS.get(v, {}).get("external_ids", []))
        return _list_filter_to_cql(field_id, vs)

    else:
        return _list_filter_to_cql(field_id, values)


def _date_filter_to_cql(field_id, date_range):
    if len(date_range) != 2:
        return None

    date_range = [datetime.strptime(d, _DATE_FORMAT)
                  if d else None for d in date_range]

    date_from, date_to = [d.strftime(_EDUREP_DATE_FORMAT)
                          if d else None for d in date_range]

    conditions = []
    if date_from:
        conditions.append('({} >= "{}")'.format(field_id, date_from))
    if date_to:
        conditions.append('({} <= "{}")'.format(field_id, date_to))
    return " AND ".join(conditions)


def _list_filter_to_cql(field_id, values):
    return " OR ".join(['({} exact "{}")'.format(field_id, v)
                        for v in values])


def _tech_format_filter_to_cql(field_id, values):
    return _aggregate_filed_filter_to_cql(field_id, values,
                                          TECH_FORMAT_MIME_TYPES)


def _custom_theme_filter_to_cql(field_id, values):
    return _aggregate_filed_filter_to_cql(field_id, values,
                                          CUSTOM_THEME_DISCIPLINES)


def _aggregate_filed_filter_to_cql(field_id, values, aggregate_field_items):
    items = list()
    for v in values:
        if v not in aggregate_field_items:
            continue
        v_cqls = ['({} exact "{}")'.format(field_id, item)
                  for item in aggregate_field_items.get(v, [])]
        items.extend(v_cqls)
    return " OR ".join(items) if items else None
