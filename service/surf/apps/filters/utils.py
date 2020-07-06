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
    EDUCATIONAL_LEVEL_FIELD_ID
)

IGNORED_FIELDS = {PUBLISHER_DATE_FIELD_ID,
                  CUSTOM_THEME_FIELD_ID
                  }

_MBO_HBO_WO_REGEX = re.compile(r"^(MBO|HBO|WO)(.*)$", re.IGNORECASE)
_HBO_WO_REGEX = re.compile(r"^(HBO|WO)(.*)$", re.IGNORECASE)


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
