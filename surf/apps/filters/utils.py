"""
This module contains some common functions for filters app.
"""

import datetime
import re
from collections import OrderedDict

from django.conf import settings
from django.db.models import Count
from tqdm import tqdm

from surf.apps.filters.models import (
    FilterCategory,
    FilterCategoryItem,
    MpttFilterItem
)
from surf.apps.locale.models import Locale
from surf.apps.themes.models import Theme
from surf.vendor.edurep.widget_endpoint.v3.api import WidgetEndpointApiClient
from surf.vendor.edurep.xml_endpoint.v1_2.api import (
    XmlEndpointApiClient,
    PUBLISHER_DATE_FIELD_ID,
    CUSTOM_THEME_FIELD_ID,
    DISCIPLINE_FIELD_ID,
    COPYRIGHT_FIELD_ID,
    EDUCATIONAL_LEVEL_FIELD_ID,
    LANGUAGE_FIELD_ID
)
from surf.vendor.edurep.xml_endpoint.v1_2.choices import (
    CUSTOM_THEME_DISCIPLINES,
    DISCIPLINE_ENTRIES
)

IGNORED_FIELDS = {PUBLISHER_DATE_FIELD_ID,
                  CUSTOM_THEME_FIELD_ID,
                  LANGUAGE_FIELD_ID
                  }

_MBO_HBO_WO_REGEX = re.compile(r"^(MBO|HBO|WO)(.*)$", re.IGNORECASE)
_HBO_WO_REGEX = re.compile(r"^(HBO|WO)(.*)$", re.IGNORECASE)

_DISCIPLINE_FILTER = "{}:0".format(DISCIPLINE_FIELD_ID)

_MAX_DISCIPLINES_IN_FILTER = 20


def get_material_count_by_disciplines(discipline_ids):
    """
    Returns the number of materials for each discipline
    :param discipline_ids: identifiers if disciplines in EduRep
    :return: dictionary with number of materials in EduRep for each discipline
    """

    rv = dict()

    # add default filters to search materials
    filters = add_default_material_filters()

    ac = XmlEndpointApiClient(api_endpoint=settings.EDUREP_XML_API_ENDPOINT)

    discipline_ids = list(discipline_ids)
    while discipline_ids:
        # request drilldowns only for part of disciplines
        if len(discipline_ids) > _MAX_DISCIPLINES_IN_FILTER:
            ds = discipline_ids[:_MAX_DISCIPLINES_IN_FILTER:]
            discipline_ids = discipline_ids[_MAX_DISCIPLINES_IN_FILTER::]
        else:
            ds, discipline_ids = discipline_ids, []

        fs = [dict(external_id=DISCIPLINE_FIELD_ID, items=ds)]
        fs.extend(filters)

        drilldowns = ac.drilldowns([_DISCIPLINE_FILTER], filters=fs)
        if drilldowns:
            drilldowns = drilldowns.get("drilldowns", [])
            for f in drilldowns:
                if f["external_id"] == DISCIPLINE_FIELD_ID:
                    drilldowns = {item["external_id"]: item["count"]
                                  for item in f["items"]}
                    break
            else:
                drilldowns = None
        if drilldowns:
            rv.update({k: drilldowns[k] for k in ds if k in drilldowns})

    return rv


def add_default_filters(filters):
    """
    Adds default filters to search materials in EduRep
    :param filters: current filters
    :return: updated list of filters
    """

    filter_categories = {f.get("external_id"): f.get("items", [])
                         for f in filters}

    # add default filters for Educational Level if needed
    if not filter_categories.get(EDUCATIONAL_LEVEL_FIELD_ID):
        items = FilterCategoryItem.objects.filter(
            category__edurep_field_id=EDUCATIONAL_LEVEL_FIELD_ID).all()
        items = [it.external_id for it in items
                 if _HBO_WO_REGEX.match(it.title)]

        filters.append(
            dict(external_id=EDUCATIONAL_LEVEL_FIELD_ID, items=items))

    # add default filters for Copyrights if needed
    if not filter_categories.get(COPYRIGHT_FIELD_ID):
        items = FilterCategoryItem.objects.filter(
            category__edurep_field_id=COPYRIGHT_FIELD_ID).all()
        items = [it.external_id for it in items]
        filters.append(dict(external_id=COPYRIGHT_FIELD_ID, items=items))

    return filters


def add_default_material_filters(filters=None, tree=None):
    """
    Adds the default enabled filters to the supplied list of filters
    :param filters: list of filters to be extended, or None to get the full list of default filters,
    :param tree: mptt filter category item tree to use instead of querying the database
    :return: the extended list of filters (or the same list if none are enabled by default)
    """
    if not filters:
        filters = []
    if not tree:
        tree = MpttFilterItem.objects.get_cached_trees()
    
    filters_external_id_list = [filter_item['external_id'] for filter_item in filters]
    for root in tree:
        # if the root.external_id (e.g. educational_level) is in the user-selected filters,
        # then don't add the default filters for that root
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


def check_and_update_filters():
    """
    Updates filter categories and their items in database
    """

    ac = None

    qs = FilterCategory.objects
    qs = qs.annotate(item_count=Count('items'))
    qs = qs.filter(item_count=0)
    for f_category in qs.all():
        if f_category.edurep_field_id in IGNORED_FIELDS:
            continue

        if not ac:
            ac = WidgetEndpointApiClient(
                api_endpoint=settings.EDUREP_JSON_API_ENDPOINT)

        _update_filter_category(f_category, ac)


def check_and_update_mptt_filters():
    """
    Updates filter categories and their items in database
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


def update_filter_category(filter_category):
    """
    Updates filter category and its items
    :param filter_category: filter category DB instance
    """

    ac = WidgetEndpointApiClient(
        api_endpoint=settings.EDUREP_JSON_API_ENDPOINT)

    if filter_category.edurep_field_id == CUSTOM_THEME_FIELD_ID:
        _update_themes(filter_category)

    elif filter_category.edurep_field_id == DISCIPLINE_FIELD_ID:
        _update_filter_category(filter_category, ac)
        _update_themes_disciplines(filter_category)

    elif filter_category.edurep_field_id not in IGNORED_FIELDS:
        _update_filter_category(filter_category, ac)


def _update_themes(theme_category):
    """
    Updates all themes and their disciplines in database
    :param theme_category: DB instance of Theme filter category
    """

    for theme_id, disciplines in CUSTOM_THEME_DISCIPLINES.items():
        # get or create Theme category item

        ci, _ = FilterCategoryItem.objects.get_or_create(
            category_id=theme_category.id,
            external_id=theme_id,
            defaults=dict(title=theme_id))

        # get or create theme
        t, _ = Theme.objects.get_or_create(external_id=theme_id)

        # relate theme with category item
        t.filter_category_item = ci
        t.save()

        # set theme disciplines
        ds = []
        for d in disciplines:
            d = FilterCategoryItem.objects.filter(
                category__edurep_field_id=DISCIPLINE_FIELD_ID,
                external_id=d).first()
            if d:
                ds.append(d)
        t.disciplines.set(ds)


def _update_themes_disciplines(discipline_category):
    """
    Updates all disciplines related to themes in database
    :param discipline_category: DB instance of Discipline filter category
    """

    for d in DISCIPLINE_ENTRIES:
        # get or create Discipline category item
        FilterCategoryItem.objects.get_or_create(
            category_id=discipline_category.id,
            external_id=d["id"],
            defaults=dict(title=d["name"]))


def _update_filter_category(filter_category, api_client):
    """
    Updates filter category according to data received from EduRep
    :param filter_category: filter category DB instance
    :param api_client: api client to EduRep
    """

    category_id = filter_category.edurep_field_id
    drilldown_name = "{}:{}".format(category_id,
                                    filter_category.max_item_count)

    res = api_client.drilldowns([drilldown_name],
                                filters=add_default_material_filters())

    items = res.get(category_id)
    if not items:
        return

    if category_id.endswith(".id"):
        _update_nested_items(filter_category, items)

    else:
        for k, v in items.items():
            if isinstance(v, dict):
                _update_category_item(filter_category, k, v["human"])
            else:
                _update_category_item(filter_category, k, k)


def _update_mptt_filter_category(filter_category, api_client):
    """
    Updates filter category according to data received from EduRep
    :param filter_category: filter category DB instance
    :param api_client: api client to EduRep
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


def _update_nested_items(filter_category, items):
    for item in items:
        _update_category_item(filter_category,
                              item["identifier"],
                              item["caption"])
        children = item.get("children")
        if children:
            _update_nested_items(filter_category, children)


def _update_nested_mptt_items(filter_category, items):
    for item in tqdm(items):
        _update_mptt_category_item(filter_category,
                              item["identifier"],
                              item["caption"])
        children = item.get("children")
        if children:
            _update_nested_mptt_items(filter_category, children)


def _update_category_item(filter_category, item_id, item_title):
    if not _is_valid_category_item(filter_category, item_id, item_title):
        return

    FilterCategoryItem.objects.get_or_create(
        category_id=filter_category.id,
        external_id=item_id,
        defaults=dict(title=item_title))


def _update_mptt_category_item(filter_category, item_id, item_title):
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
    if filter_category.external_id != EDUCATIONAL_LEVEL_FIELD_ID and item_id != 'no':
        return True

    return _MBO_HBO_WO_REGEX.match(item_title) is not None


def _is_valid_category_item(filter_category, item_id, item_title):
    if filter_category.edurep_field_id != EDUCATIONAL_LEVEL_FIELD_ID:
        return True

    return _MBO_HBO_WO_REGEX.match(item_title) is not None
