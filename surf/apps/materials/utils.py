"""
This module contains some common functions for materials app.
"""

import json

from django.conf import settings

from surf.apps.communities.models import Community
from surf.apps.filters.models import MpttFilterItem
from surf.apps.materials.models import (
    Material,
)
from surf.apps.themes.models import Theme
from surf.vendor.edurep.xml_endpoint.v1_2.api import (
    DISCIPLINE_FIELD_ID,
    CUSTOM_THEME_FIELD_ID
)
from surf.vendor.search.searchselector import get_search_client


def update_materials_data(materials):
    """
    Updates materials extra data from EduRep
    :param materials: list of material DB instances
    """

    for material in materials:
        details = get_material_details_by_id(material.external_id)
        if not details:
            continue

        try:
            m = details[0]
            material.material_url = m.get("url")
            material.title = m.get("title")
            material.description = m.get("description")
            keywords = m.get("keywords")
            if keywords:
                keywords = json.dumps(keywords)
            material.keywords = keywords
            material.save()

            add_material_themes(material, m.get("themes", []))
            add_material_disciplines(material, m.get("disciplines", []))

        except IndexError:
            pass


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
    :param user: user who requested material
    :param materials: array of materials
    :return: updated array of materials
    """
    # perhaps this could be optimized by querying the database once for a list of materials
    # however, we still want to add the 0 values for items we don't have in the database yet so this is easy for now
    for m in materials:

        material_object = Material.objects.filter(external_id=m["external_id"])
        if material_object:
            material_object = material_object[0]

            m["view_count"] = material_object.view_count
            m["applaud_count"] = material_object.applaud_count
            m["avg_star_rating"] = material_object.get_avg_star_rating()
            m["count_star_rating"] = material_object.get_star_count()
        else:
            m["view_count"] = m["applaud_count"] = m["avg_star_rating"] = m["count_star_rating"] = 0

        communities = Community.objects.filter(
            collections__materials__external_id=m["external_id"])

        m["communities"] = [dict(id=c.id, name=c.name) for c in
                            communities.distinct().all()]

    return materials


_DISCIPLINE_FILTER = "{}:0".format(DISCIPLINE_FIELD_ID)


def get_material_details_by_id(material_id, api_client=None):
    """
    Request from EduRep and return details of material by its EduRep id
    :param material_id: id of material in EduRep
    :param api_client: EduRep API client (optional)
    :return: list of requested materials
    """

    if not api_client:
        api_client = get_search_client()

    res = api_client.get_materials_by_id([material_id], drilldown_names=[_DISCIPLINE_FILTER])

    # define themes and disciplines for requested material
    themes = []
    disciplines = []
    for f in res.get("drilldowns", []):
        if f["external_id"] == CUSTOM_THEME_FIELD_ID:
            themes = [item["external_id"] for item in f["items"]]
        elif f["external_id"] == DISCIPLINE_FIELD_ID:
            disciplines = [item["external_id"] for item in f["items"]]

    # set extra details for requested material
    rv = res.get("records", [])
    for material in rv:
        material["themes"] = themes
        material["disciplines"] = disciplines

        m = Material.objects.filter(external_id=material_id).first()
        if m:
            material["number_of_collections"] = m.collections.count()

    return rv
