"""
This module provides Django REST API filters for communities app.
"""

from django_filters import rest_framework as filters
from django_filters import CharFilter

from surf.apps.communities.models import Community


class CommunityFilter(filters.FilterSet):
    """
    Provides filtering functionality for communities requests
    """

    material_id = CharFilter(field_name='collections__materials__external_id')

    class Meta:
        model = Community
        fields = ('material_id', )
