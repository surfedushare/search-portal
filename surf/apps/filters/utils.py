from django.db.models import Count

from surf.vendor.edurep.widget_endpoint.v3.api import WidgetEndpointApiClient

from surf.vendor.edurep.xml_endpoint.v1_2.api import (
    PUBLISHER_DATE_FILED_ID,
    CUSTOM_THEME_FIELD_ID
)

from surf.apps.filters.models import FilterCategory, FilterCategoryItem

IGNORED_FIELDS = {PUBLISHER_DATE_FILED_ID,
                  CUSTOM_THEME_FIELD_ID}


def check_and_update_filters():
    ac = None

    qs = FilterCategory.objects
    qs = qs.annotate(item_count=Count('items'))
    qs = qs.filter(item_count=0)
    for f_category in qs.all():
        if f_category.edurep_field_id in IGNORED_FIELDS:
            continue

        if not ac:
            ac = WidgetEndpointApiClient()
        _update_filter_category(f_category, ac)


def update_filter_category(filter_category):
    ac = WidgetEndpointApiClient()
    if filter_category.edurep_field_id not in IGNORED_FIELDS:
        _update_filter_category(filter_category, ac)


def _update_filter_category(filter_category, api_client):
    category_id = filter_category.edurep_field_id
    drilldown_name = "{}:{}".format(category_id,
                                    filter_category.max_item_count)

    res = api_client.drilldowns([drilldown_name])
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


def _update_nested_items(filter_category, items):
    for item in items:
        _update_category_item(filter_category,
                              item["identifier"],
                              item["caption"])
        children = item.get("children")
        if children:
            _update_nested_items(filter_category, children)


def _update_category_item(filter_category, item_id, item_title):
    FilterCategoryItem.objects.get_or_create(
        category_id=filter_category.id,
        external_id=item_id,
        defaults=dict(category=filter_category,
                      external_id=item_id,
                      title=item_title))
