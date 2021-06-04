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
from surf.vendor.search.choices import AUTHOR_FIELD_ID, PUBLISHER_FIELD_ID


logger = logging.getLogger("service")


EDUTERM_QUERY_TEMPLATE = "http://api.onderwijsbegrippen.kennisnet.nl/1.0/Query/GetConcept" \
                         "?format=json&apikey={api_key}&concept=<http://purl.edustandaard.nl/concept/{concept}>"

EDUSTANDAARD_TEMPLATE = "{protocol}://purl.edustandaard.nl/begrippenkader/{concept}"

DEEPL_ENDPOINT = "https://api-free.deepl.com/v2/translate"

ENGLISH_SAME_AS_DUTCH = [AUTHOR_FIELD_ID, PUBLISHER_FIELD_ID]


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
            is_new = True

            if filter_category.external_id in ENGLISH_SAME_AS_DUTCH:
                _auto_enable_english_same_as_dutch(filter_item)
            else:
                _translate_mptt_filter_item(filter_item)

        yield external_id, is_new


def _auto_enable_english_same_as_dutch(filter_item):
    translation = Locale.objects.create(
        asset=f"{filter_item.external_id}_auto_generated_at_{datetime.datetime.now().strftime('%c-%f')}",
        en=filter_item.external_id, nl=filter_item.external_id, is_fuzzy=True
    )
    filter_item.name = filter_item.external_id
    filter_item.title_translations = translation
    filter_item.is_hidden = False
    filter_item.save()


def _translate_mptt_filter_item(filter_item):
    translations = _fetch_eduterm_translations(filter_item.external_id)

    if not translations:
        translations = _fetch_edustandaard_translations(filter_item.external_id)

    if translations:
        _save_translations(filter_item, translations[0], translations[1])


def _fetch_eduterm_translations(external_id):
    query_url = EDUTERM_QUERY_TEMPLATE.format(concept=external_id, api_key=settings.EDUTERM_API_KEY)
    response = requests.get(query_url)

    if response.status_code != codes.ok:
        return

    labels = response.json()["results"]["bindings"]
    if not len(labels):
        return

    default = labels[0]["label"]
    dutch = labels[0].get("label_nl", default)
    english = labels[0].get("label_en", default)

    if english['value'] == dutch['value']:
        translated = _translate_with_deepl(dutch['value'])
        return dutch['value'], translated

    return dutch['value'], english['value']


def _fetch_edustandaard_translations(external_id):
    query_url = EDUSTANDAARD_TEMPLATE.format(concept=external_id, protocol="https")
    headers = {'Accept': 'application/json'}
    response = requests.get(query_url, headers=headers)

    if response.status_code != codes.ok:
        return

    json = response.json()
    key = EDUSTANDAARD_TEMPLATE.format(concept=external_id, protocol="http")

    if not json.get(key, None):
        return

    dutch_value = json[key]['http://www.w3.org/2004/02/skos/core#prefLabel'][0]['value']

    english_value = _translate_with_deepl(dutch_value)

    return dutch_value, english_value


def _save_translations(filter_item, nl_value, en_value):
    translation = Locale.objects.create(
        asset=f"{en_value}_auto_generated_at_{datetime.datetime.now().strftime('%c-%f')}",
        en=en_value, nl=nl_value, is_fuzzy=True
    )
    filter_item.name = en_value
    filter_item.title_translations = translation
    filter_item.save()


def _translate_with_deepl(dutch_value):
    if not settings.DEEPL_API_KEY:
        return dutch_value

    response = requests.post(DEEPL_ENDPOINT, {
        'auth_key': [settings.DEEPL_API_KEY],
        'text': dutch_value,
        'source_lang': "NL",
        'target_lang': "EN"
    })

    if response.status_code != codes.ok:
        return dutch_value

    json = response.json()
    return json['translations'][0]['text']
