import json

from django.conf import settings

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
