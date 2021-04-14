"""
This module contains some common functions for filters app.
"""
import datetime
import requests
from requests.status_codes import codes
import logging

from django.conf import settings
from django.db import models

from surf.vendor.elasticsearch.api import ElasticSearchApiClient
from surf.apps.filters.models import MpttFilterItem
from surf.apps.locale.models import Locale
from surf.vendor.search.choices import AUTHOR_FIELD_ID


logger = logging.getLogger("service")


EDUTERM_QUERY_TEMPLATE = "http://api.onderwijsbegrippen.kennisnet.nl/1.0/Query/GetConcept" \
                         "?format=json&apikey={api_key}&concept=<http://purl.edustandaard.nl/concept/{concept}>"


def sync_category_filters():
    """
    Updates all filter categories and their items in database according to information from Elastic Search.
    """

    filter_categories = MpttFilterItem.objects.exclude(is_manual=True)

    ac = ElasticSearchApiClient()
    valid_external_ids = []
    has_new = False

    for f_category in filter_categories.filter(parent=None):
        valid_external_ids.append(f_category.external_id)
        logger.info(f"Filter category name: {f_category.name}")
        for external_id, is_new in _update_mptt_filter_category(f_category, ac):
            if is_new:
                has_new = True
            valid_external_ids.append(external_id)

    logger.info("Deleting redundant filters and translations")
    filter_categories.exclude(external_id__in=valid_external_ids).delete()
    Locale.objects \
        .annotate(filter_count=models.Count("mpttfilteritem")) \
        .filter(asset__contains="auto_generated_at", filter_count=0, is_fuzzy=True) \
        .delete()

    logger.info("Finished Update")
    return has_new


def _translate_mptt_filter_item(filter_item):
    query_url = EDUTERM_QUERY_TEMPLATE.format(concept=filter_item.external_id, api_key=settings.EDUTERM_API_KEY)
    response = requests.get(query_url)
    if response.status_code != codes.ok:
        return
    labels = response.json()["results"]["bindings"]
    if not len(labels):
        return
    default = labels[0]["label"]
    dutch = labels[0].get("label_nl", default)
    english = labels[0].get("label_en", default)
    translation = Locale.objects.create(
        asset=f"{english['value']}_auto_generated_at_{datetime.datetime.now().strftime('%c-%f')}",
        en=english["value"], nl=dutch["value"], is_fuzzy=True
    )
    filter_item.name = english["value"]
    filter_item.title_translations = translation
    filter_item.save()


def _auto_enable_mptt_filter_item(filter_item):
    translation = Locale.objects.create(
        asset=f"{filter_item.external_id}_auto_generated_at_{datetime.datetime.now().strftime('%c-%f')}",
        en=filter_item.external_id, nl=filter_item.external_id, is_fuzzy=True
    )
    filter_item.name = filter_item.external_id
    filter_item.title_translations = translation
    filter_item.is_hidden = False
    filter_item.save()


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
        is_new = False
        filter_item, created = MpttFilterItem.objects.get_or_create(
            external_id=external_id,
            defaults={
                "name": external_id,
                "parent": filter_category,
                "is_hidden": True
            }
        )
        if created or filter_item.title_translations is None:
            if external_id == AUTHOR_FIELD_ID:
                _auto_enable_mptt_filter_item(filter_item)
            else:
                _translate_mptt_filter_item(filter_item)
            is_new = True

        yield external_id, is_new
