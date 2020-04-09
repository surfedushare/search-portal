"""
This module provides Django REST API filters for themes app.
"""

from django_filters import rest_framework as filters
from django_filters import CharFilter

from surf.apps.themes.models import Theme


class ThemeFilter(filters.FilterSet):
    """
    Provides filtering functionality for themes requests
    """

    discipline_id = CharFilter(field_name='disciplines__external_id')

    class Meta:
        model = Theme
        fields = ('discipline_id',)
