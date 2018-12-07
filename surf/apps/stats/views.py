from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from django.conf import settings

from surf.apps.filters.utils import get_all_materials_filters
from surf.vendor.edurep.xml_endpoint.v1_2.api import XmlEndpointApiClient


class StatsView(ViewSet):
    """
    View class that provides statistics information.
    """

    permission_classes = []

    @action(methods=['get'], url_path="all-materials", detail=False)
    def all_materials(self, request, **kwargs):
        """
        Returns the number of all available materials
        """

        ac = XmlEndpointApiClient(
            api_endpoint=settings.EDUREP_XML_API_ENDPOINT)

        filters = get_all_materials_filters()
        res = ac.search([], filters=filters, page_size=0)
        return Response(dict(value=res.get("recordcount", 0)))
