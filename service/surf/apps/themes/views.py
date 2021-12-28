"""
This module contains implementation of REST API views for themes app.
"""
from rest_framework.viewsets import GenericViewSet

from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from surf.apps.themes.models import Theme
from surf.apps.themes.serializers import ThemeSerializer
from surf.apps.themes.filters import ThemeFilter


_COLLECTIONS_COUNT_IN_OVERVIEW = 4


class ThemeViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    View class that provides `GET` method for Themes.
    """

    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    filter_class = ThemeFilter
    permission_classes = []
    lookup_field = 'filter_category_item__id'
