"""
This module contains some common functions for materials app.
"""

import datetime
from functools import reduce

from surf.apps.communities.models import Community
from surf.apps.filters.models import MpttFilterItem
from surf.apps.materials.models import (
    Material,
)
from surf.apps.themes.models import Theme
from surf.vendor.elasticsearch.api import ElasticSearchApiClient


def add_material_themes(material, themes):
    ts = Theme.objects.filter(external_id__in=themes).all()
    material.themes.set(ts)


def add_material_disciplines(material, disciplines):
    ds = MpttFilterItem.objects.filter(external_id__in=disciplines).all()
    material.disciplines.set(ds)


def add_extra_parameters_to_materials(user, materials):
    """
    Add additional parameters for materials (bookmark, number of applauds,
    number of views)
    NB: this gets added to deleted materials as well, but as they were being found still that seems good

    :param user: user who requested material
    :param materials: array of materials
    :return: updated array of materials
    """

    material_objects = {
        material.external_id: material
        for material in Material.objects.filter(external_id__in=(m["external_id"] for m in materials))
    }

    educational_level_filters = {
        filter_item.external_id: filter_item
        for filter_item in MpttFilterItem.objects.filter(
            name__in=(level for material in materials for level in material["educationallevels"])
        ).distinct().select_related("title_translations")
    }

    discipline_filters = {
        filter_item.external_id: filter_item
        for filter_item in MpttFilterItem.objects.filter(
            external_id__in=(discipline for material in materials for discipline in material["disciplines"])
        ).distinct().select_related("title_translations")

    }

    for m in materials:
        material_object = material_objects.get(m["external_id"], None)

        if material_object:
            m["view_count"] = material_object.view_count
            m["applaud_count"] = material_object.applaud_count
            m["avg_star_rating"] = material_object.get_avg_star_rating()
            m["count_star_rating"] = material_object.get_star_count()
        else:
            m["view_count"] = m["applaud_count"] = m["avg_star_rating"] = m["count_star_rating"] = 0

        educational_levels = filter(
            None,
            [educational_level_filters.get(external_id, None) for external_id in m["educationallevels"]]
        )
        m["educationallevels"] = [
            {
                "en": educational_level.title_translations.en,
                "nl": educational_level.title_translations.nl
            }
            for educational_level in educational_levels
        ]

        communities = Community.objects.filter(
            collections__materials__external_id=m["external_id"])

        m["communities"] = [dict(id=c.id, name=c.name) for c in communities.distinct().all()]

        disciplines = filter(
            None,
            [discipline_filters.get(external_id, None) for external_id in m["disciplines"]]
        )

        m["disciplines"] = [dict(
            id=d.id,
            title_translations={"nl": d.title_translations.nl, "en": d.title_translations.en} if d.title_translations
            else {"nl": d.name, "en": d.name}
        ) for d in disciplines]

        m["authors"] = [author["name"] for author in m["authors"]]

    return materials


def get_material_details_by_id(external_id):
    """
    Request from ES and return details of material by its id

    :param external_id: id of material
    :return: list containing updated material
    """
    api_client = ElasticSearchApiClient()
    response = api_client.get_materials_by_id([external_id])
    records = response.get("records", [])
    if not records:
        return records

    material = records[0]
    details = Material.objects.filter(external_id=external_id, deleted_at=None).first()
    material["number_of_collections"] = details.collections.filter(deleted_at=None).count() if details else 0
    return [material]


def create_search_results_index(client):
    body = {
        'mappings': {
            'date_detection': False,
            'properties': {
                'timestamp': {
                    'type': 'date'
                },
                'number_of_results': {
                    'type': 'integer'
                },
                'query': {
                    'type': 'text',
                    'fields': {
                        'keyword': {
                            'type': 'keyword'
                        }
                    }
                },
                'filters': {
                    'type': 'nested',
                    'properties': {
                        'name': {
                            'type': 'keyword'
                        },
                        'values': {
                            'type': 'keyword'
                        }
                    }
                }

            }
        }
    }
    client.indices.create('search-results', body=body)


def add_search_query_to_elastic_index(number_of_results, query, filters):
    elastic = ElasticSearchApiClient()
    if not elastic.client.indices.exists(index='search-results'):
        create_search_results_index(elastic.client)

    document = {
        'timestamp': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
        'number_of_results': number_of_results,
        'query': query,
        'filters': _get_translated_filters(filters)
    }
    elastic.client.index('search-results', body=document)


def _get_translated_filters(filters):
    def append_external_ids(memo, filter):
        filter_list = list(filter.items())
        name = filter_list[0][1]
        memo.append(name)
        items = filter_list[1][1]
        for item in items:
            memo.append(item)
        return memo

    external_ids = reduce(append_external_ids, filters, [])
    filter_items = {
        filter_item.external_id: filter_item
        for filter_item in MpttFilterItem.objects.filter(
            external_id__in=external_ids
        ).select_related("title_translations").all()
    }

    def add_translated_filter(memo, filter_item):
        filter_list = list(filter_item.items())
        external_id = filter_list[0][1]
        filter_item_external_id = filter_items.get(external_id, None)
        items = filter_list[1][1]
        name = filter_item_external_id.title_translations.en if filter_item_external_id else external_id
        translated_items = [
            filter_items.get(item).title_translations.en
            if filter_items.get(item, None) else item for item in items
        ]

        memo.append({
            'name': name,
            'values': translated_items
        })
        return memo

    return reduce(add_translated_filter, filters, [])
