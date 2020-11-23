"""
This module provides integration with XML-based endpoint of EduRep API.
"""

from datetime import datetime

import logging

from surf.vendor.search.choices import (
    TECH_FORMAT_MIME_TYPES,
    CUSTOM_THEME_DISCIPLINES,
)

logger = logging.getLogger()

TECH_FORMAT_FIELD_ID = "lom.technical.format"
CUSTOM_THEME_FIELD_ID = "custom_theme.id"
DISCIPLINE_FIELD_ID = "lom.classification.obk.discipline.id"
COPYRIGHT_FIELD_ID = "lom.rights.copyrightandotherrestrictions"
LANGUAGE_FIELD_ID = "lom.general.language"
AUTHOR_FIELD_ID = "lom.lifecycle.contribute.author"
PUBLISHER_FIELD_ID = "lom.lifecycle.contribute.publisher"
PUBLISHER_DATE_FIELD_ID = "lom.lifecycle.contribute.publisherdate"
EDUCATIONAL_LEVEL_FIELD_ID = "lom.classification.obk.educationallevel.id"


_DATE_TYPE_FIELDS = {PUBLISHER_DATE_FIELD_ID}

_DATE_FORMAT = "%Y-%m-%d"
_EDUREP_DATE_FORMAT = "%Y%m%d"


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
        return _custom_theme_filter_to_cql(DISCIPLINE_FIELD_ID, values)

    elif field_id == COPYRIGHT_FIELD_ID:
        return _list_filter_to_cql(field_id, values)

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
