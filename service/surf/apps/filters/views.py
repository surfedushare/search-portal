"""
This module contains implementation of REST API views for filters app.
"""

from types import SimpleNamespace

from rest_framework import status, generics
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from surf.apps.filters.models import MpttFilterItem
from surf.apps.filters.serializers import MpttFilterItemSerializer
from surf.apps.materials.views import MaterialSearchAPIView


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
