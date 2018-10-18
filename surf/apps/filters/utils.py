from django.db.models import Count

from surf.vendor.edurep.widget_endpoint.v3.api import WidgetEndpointApiClient

from surf.apps.filters.models import FilterCategory, FilterCategoryItem

_IGNORED_UPDATE_FIELDS = set("lom.lifecycle.contribute.publisherdate")


def check_and_update_filters():
    ac = None

    qs = FilterCategory.objects
    qs = qs.annotate(item_count=Count('items'))
    qs = qs.filter(item_count=0)
    for f_category in qs.all():
        if f_category.edurep_field_id in _IGNORED_UPDATE_FIELDS:
            continue

        if not ac:
            ac = WidgetEndpointApiClient()
        _update_filter_category(f_category, ac)


def _update_filter_category(filter_category, api_client):
    category_id = filter_category.edurep_field_id
    drilldown_name = "{}:{}".format(category_id,
                                    filter_category.max_item_count)

    res = api_client.drilldowns([drilldown_name])
    items = res.get(category_id)
    if not items:
        return

    if category_id.endswith(".id"):
        for item in items:
            _update_category_item(filter_category,
                                  item["identifier"],
                                  item["caption"])

    else:
        for k, v in items.items():
            if isinstance(v, dict):
                _update_category_item(filter_category, k, v["human"])
            else:
                _update_category_item(filter_category, k, k)


def _update_category_item(filter_category, item_id, item_title):
    FilterCategoryItem.objects.get_or_create(
        category_id=filter_category.id,
        external_id=item_id,
        defaults=dict(category=filter_category,
                      external_id=item_id,
                      title=item_title))
