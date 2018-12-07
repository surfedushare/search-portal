"""
This module contains some common functions for materials app.
"""

import json

from django.conf import settings

from surf.apps.materials.models import (
    Material,
    ApplaudMaterial,
    ViewMaterial
)

from surf.vendor.edurep.xml_endpoint.v1_2.api import XmlEndpointApiClient


def update_materials_data(materials):
    """
    Updates materials extra data from EduRep
    :param materials: list of material DB instances
    """

    ac = XmlEndpointApiClient(
        api_endpoint=settings.EDUREP_XML_API_ENDPOINT)

    for material in materials:
        res = ac.get_materials_by_id(['"{}"'.format(material.external_id)])
        if not res:
            continue

        try:
            m = res.get("records", [])[0]
            material.material_url = m.get("url")
            material.title = m.get("title")
            material.description = m.get("description")
            keywords = m.get("keywords")
            if keywords:
                keywords = json.dumps(keywords)
            material.keywords = keywords
            material.save()
        except IndexError:
            pass


def add_extra_parameters_to_materials(user, materials):
    """
    Add additional parameters for materials (bookmark, number of applauds,
    number of views)
    :param user: user who requested material
    :param materials: array of materials
    :return: updated array of materials
    """
    for m in materials:
        if user and user.id:
            qs = Material.objects.prefetch_related("collections")
            qs = qs.filter(collections__owner_id=user.id,
                           external_id=m["external_id"])
            m["has_bookmark"] = qs.exists()

        qs = ApplaudMaterial.objects.prefetch_related("material")
        qs = qs.filter(material__external_id=m["external_id"])
        m["number_of_applauds"] = qs.count()

        qs = ViewMaterial.objects.prefetch_related("material")
        qs = qs.filter(material__external_id=m["external_id"])
        m["number_of_views"] = qs.count()

    return materials
