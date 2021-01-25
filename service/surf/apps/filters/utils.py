"""
This module contains some common functions for filters app.
"""
import datetime

from django.db import models

from surf.apps.filters.models import (
    MpttFilterItem
)
from surf.apps.locale.models import Locale
from surf.vendor.elasticsearch.api import ElasticSearchApiClient


MANUAL_FILTER_CATEGORIES = {
    "lom.lifecycle.contribute.publisherdate",
    "custom_theme.id",
    "lom.general.language",
    "lom.rights.copyrightandotherrestrictions",
}


def check_and_update_mptt_filters():
    """
    Updates all filter categories and their items in database according to information from Elastic Search.
    """

    # First we create a queryset that only targets all non-manual filter categories
    # We ignore any manual filter categories and their children (up to two levels deep)
    filter_categories = MpttFilterItem.objects.exclude(external_id__in=MANUAL_FILTER_CATEGORIES)
    filter_categories = filter_categories.exclude(parent__external_id__in=MANUAL_FILTER_CATEGORIES)
    filter_categories = filter_categories.exclude(parent__parent__external_id__in=MANUAL_FILTER_CATEGORIES)

    ac = ElasticSearchApiClient()
    valid_external_ids = []

    for f_category in filter_categories.filter(parent=None):
        valid_external_ids.append(f_category.external_id)
        print(f"Filter category name: {f_category.name}")
        for external_id in _update_mptt_filter_category(f_category, ac):
            valid_external_ids.append(external_id)

    print("Deleting redundant filters and translations")
    filter_categories.exclude(external_id__in=valid_external_ids).delete()
    Locale.objects \
        .annotate(filter_count=models.Count("mpttfilteritem")) \
        .filter(asset__contains="auto_generated_at", filter_count=0, is_fuzzy=True) \
        .delete()

    print("Finished Update")


def _update_mptt_filter_category(filter_category, api_client):
    """
    Updates filter category according to data received from EduRep
    :param filter_category: filter category DB instance to be updated
    :param api_client: api client instance to connect EduRep
    """
    response = api_client.drilldowns([filter_category.external_id], filters=None)
    filters = {
        item["external_id"]: item["count"]
        for item in response["drilldowns"][0]["items"]
    }
    for external_id, count in filters.items():
        filter_item, created = MpttFilterItem.objects.get_or_create(
            external_id=external_id,
            defaults={
                "name": external_id,
                "parent": filter_category,
            }
        )
        if created or filter_item.title_translations is None:
            translation = Locale.objects.create(
                asset=f"{external_id}_auto_generated_at_{datetime.datetime.now().strftime('%c-%f')}",
                en=external_id, nl=external_id, is_fuzzy=True
            )
            filter_item.title_translations = translation
            filter_item.save()

        yield external_id
