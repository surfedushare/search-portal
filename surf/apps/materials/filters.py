"""
This module provides Django REST API filters for materials app.
"""

from django_filters import rest_framework as filters
from django_filters import CharFilter

from surf.apps.materials.models import ApplaudMaterial, Collection


class ApplaudMaterialFilter(filters.FilterSet):
    """
    Provides filtering functionality for Material applauds requests
    """

    class Meta:
        model = ApplaudMaterial
        fields = ('material__external_id',)


class CollectionFilter(filters.FilterSet):
    """
    Provides filtering functionality for collections requests
    """

    is_owner = CharFilter(method="filter_is_owner")
    material_id = CharFilter(method="filter_by_material_id")

    def filter_is_owner(self, qs, name, value):
        """
        Filters or excludes collections of current user
        :param qs: queryset instance
        :param name: query parameter name
        :param value: query parameter value
        :return: updated queryset of collections
        """

        user_ids = []

        if self.request:
            user = self.request.user
            if user and user.is_authenticated:
                user_ids.append(user.id)

        value = value in {True, "True", "true", "1"}
        if value:
            return qs.filter(owner_id__in=user_ids)
        else:
            return qs.exclude(owner_id__in=user_ids)

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
        fields = ('is_owner', 'material_id', 'publish_status',)
