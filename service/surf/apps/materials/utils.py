import datetime
from functools import reduce

from django.conf import settings
from django.apps import apps

from surf.apps.communities.models import Community
from surf.apps.materials.models import Material
from surf.vendor.elasticsearch.api import ElasticSearchApiClient


def add_extra_parameters_to_materials(metadata, materials):
    """
    Add additional parameters for materials (bookmark, number of applauds,
    number of views)
    NB: this gets added to deleted materials as well, but as they were being found still that seems good

    :param metadata: the metadata tree to get some extra information from
    :param materials: array of materials
    :return: updated array of materials
    """
    if settings.PROJECT != "edusources":
        return materials

    material_objects = {
        material.external_id: material
        for material in Material.objects.filter(external_id__in=(m["external_id"] for m in materials))
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

        educational_level_translations = metadata.translations["lom_educational_levels"]
        m["educationallevels"] = [
            educational_level_translations[educational_level_id]
            for educational_level_id in m.get("educationallevels", [])
        ]

        communities = Community.objects.filter(
            collections__materials__external_id=m["external_id"])

        m["communities"] = [dict(id=c.id, name=c.name) for c in communities.distinct().all()]

        discipline_translations = metadata.translations["disciplines"]
        m["disciplines"] = [
            {
                "id": discipline_id,
                "title_translations": discipline_translations[discipline_id]
            }
            for discipline_id in m["disciplines"]
        ]

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

    filters_app = apps.get_app_config("filters")
    filter_translations = filters_app.metadata.translations

    def add_translated_filter(memo, filter_item):
        field = filters_app.metadata.get_field(filter_item["external_id"])
        memo.append({
            'name': field["translation"]["en"],
            'values': [
                filter_translations[field["value"]][item]["en"]
                for item in filter_item["items"]
            ]
        })
        return memo

    return reduce(add_translated_filter, filters, [])
