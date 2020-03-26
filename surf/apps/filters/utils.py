"""
This module contains some common functions for filters app.
"""

import datetime
import re
from collections import OrderedDict

from django.conf import settings
from tqdm import tqdm

from surf.apps.filters.models import (
    MpttFilterItem
)
from surf.apps.locale.models import Locale
from surf.vendor.edurep.widget_endpoint.v3.api import WidgetEndpointApiClient
from surf.vendor.edurep.xml_endpoint.v1_2.api import (
    PUBLISHER_DATE_FIELD_ID,
    CUSTOM_THEME_FIELD_ID,
    EDUCATIONAL_LEVEL_FIELD_ID,
    LANGUAGE_FIELD_ID
)

IGNORED_FIELDS = {PUBLISHER_DATE_FIELD_ID,
                  CUSTOM_THEME_FIELD_ID,
                  LANGUAGE_FIELD_ID
                  }

_MBO_HBO_WO_REGEX = re.compile(r"^(MBO|HBO|WO)(.*)$", re.IGNORECASE)
_HBO_WO_REGEX = re.compile(r"^(HBO|WO)(.*)$", re.IGNORECASE)


def add_default_material_filters(filters=None, tree=None):
    """
    Adds the default enabled filters to the supplied list of filters.
    In the filter admin there is a check to enable a filter by default, these get used here.
    Much like a google search will default to your language unless you specifically tell it otherwise,
    this allows us to enable certain filter items like education level and copyright by default.
    :param filters: list of filters to be extended, or None to get the full list of default filters,
    :param tree: mptt filter category item tree to use instead of querying the database (to speed up the method).
    :return: the extended list of filters (or the same list if none are enabled by default)
    """
    if not filters:
        filters = []
    if not tree:
        tree = MpttFilterItem.objects.get_cached_trees()

    filters_external_id_list = [filter_item['external_id'] for filter_item in filters]
    for root in tree:
        # if the root.external_id (e.g. educational_level) is in the user-selected filters,
        # then don't add the default filters for that root. So if a user selects 'HBO', don't also default to 'WO'.
        # And if a node that is enabled by default has children, they're enabled by default as well.
        if root.external_id not in filters_external_id_list:
            enabled_children = root.get_children()
            if not root.enabled_by_default:
                enabled_children = [child for child in enabled_children if child.enabled_by_default]
            child_external_ids = []
            for child in enabled_children:
                child_external_ids.extend([grand_child.external_id for grand_child in child.get_children()])
            if enabled_children:
                # if child.external_id is empty don't append it to the filters, edurep fails on empty strings
                child_external_ids.extend([child.external_id for child in enabled_children if child.external_id])
            filters.append(OrderedDict(external_id=root.external_id, items=child_external_ids))
    return filters


def check_and_update_mptt_filters():
    """
    Updates all filter categories and their items in database according to information from Edurep.
    """

    ac = None
    qs = MpttFilterItem.objects

    for f_category in qs.all():
        if f_category.external_id in IGNORED_FIELDS:
            continue

        if not ac:
            ac = WidgetEndpointApiClient(api_endpoint=settings.EDUREP_JSON_API_ENDPOINT)
        try:
            print(f"Filter category name: {f_category.name}")
        except UnicodeEncodeError as exc:
            print(exc)
        _update_mptt_filter_category(f_category, ac)
    print("Finished Update")


def _update_mptt_filter_category(filter_category, api_client):
    """
    Updates filter category according to data received from EduRep
    :param filter_category: filter category DB instance to be updated
    :param api_client: api client instance to connect EduRep
    """

    category_id = filter_category.external_id
    print(category_id)
    drilldown_name = "{}:{}".format(category_id, 0)
    res = api_client.drilldowns([drilldown_name], filters=None)
    items = res.get(category_id)
    if not items:
        return
    if category_id.endswith(".id"):
        _update_nested_mptt_items(filter_category, items)

    else:
        for k, v in items.items():
            if isinstance(v, dict):
                _update_mptt_category_item(filter_category, k, v["human"])
            else:
                _update_mptt_category_item(filter_category, k, k)


def _update_nested_mptt_items(filter_category, items):
    """
    Recursively go through the filter category's children and update/create them if need be.
    :param filter_category: The parent category to check.
    :param items: the children to be added
    """
    for item in tqdm(items):
        _update_mptt_category_item(filter_category,
                                   item["identifier"],
                                   item["caption"])
        children = item.get("children")
        if children:
            _update_nested_mptt_items(filter_category, children)


def _update_mptt_category_item(filter_category, item_id, item_title):
    """
    Sort of 'get_or_create', however since we want to keep the tree structure intact when it's edited we check manually.
    :param filter_category: the parent of the item to be created.
    :param item_id: the external id of the filter category item
    :param item_title: the name of the filter category item
    """
    if not _is_valid_mptt_category_item(filter_category, item_id, item_title):
        return
    # normally we'd do this with a get_or_create, however since we want to leave the manually adjusted tree intact
    # we're doing it manually.
    if not MpttFilterItem.objects.filter(external_id=item_id).exists():
        translation = Locale.objects.create(
            asset=f"{item_title}_auto_generated_at_{datetime.datetime.now().strftime('%c-%f')}",
            en=item_title, nl=item_title, is_fuzzy=True)
        MpttFilterItem.objects.create(name=item_title, parent=filter_category,
                                      title_translations=translation, external_id=item_id)


def _is_valid_mptt_category_item(filter_category, item_id, item_title):
    """
    Filter some 'unwanted' items from edurep.
    """
    if filter_category.external_id != EDUCATIONAL_LEVEL_FIELD_ID and item_id != 'no':
        return True

    return _MBO_HBO_WO_REGEX.match(item_title) is not None
