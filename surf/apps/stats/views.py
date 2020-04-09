"""
This module contains implementation of REST API views for stats app.
"""

from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from surf.apps.filters.utils import add_default_material_filters
from surf.vendor.search.searchselector import get_search_client


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

        ac = get_search_client()

        filters = add_default_material_filters()
        res = ac.search([], filters=filters, page_size=0)
        return Response(dict(value=res.get("recordcount", 0)))
