"""
This module provides Django REST API filters for materials app.
"""

from django_filters import rest_framework as filters
from django_filters import CharFilter

from surf.apps.materials.models import Collection


class CollectionFilter(filters.FilterSet):
    """
    Provides filtering functionality for collections requests
    """

    material_id = CharFilter(method="filter_by_material_id")

    @staticmethod
    def filter_by_material_id(qs, name, value):
        """
        Filters collections which contain material
        :param qs: queryset instance
        :param name: query parameter name
        :param value: query parameter value (external id of material)
        :return: updated queryset
        """

        return qs.filter(materials__external_id=value)

    class Meta:
        model = Collection
        fields = ('material_id', 'publish_status',)
