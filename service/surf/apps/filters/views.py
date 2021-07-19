"""
This module contains implementation of REST API views for filters app.
"""

from rest_framework import generics
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from surf.apps.filters.models import MpttFilterItem
from surf.apps.filters.serializers import MpttFilterItemSerializer


class FilterCategoryViewSet(ListModelMixin, GenericViewSet):
    """
    Viewset class that provides `list()` action for Filter Category.
    """
    serializer_class = MpttFilterItemSerializer
    permission_classes = []

    def get_queryset(self):
        return MpttFilterItem.objects.select_related("title_translations").get_cached_trees()


class MpttFilterItems(generics.GenericAPIView):
    serializer_class = MpttFilterItemSerializer
