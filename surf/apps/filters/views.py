"""
This module contains implementation of REST API views for filters app.
"""

from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet
)

from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated

from surf.apps.filters.models import (
    FilterCategory,
    Filter
)

from surf.apps.filters.serializers import (
    FilterCategorySerializer,
    FilterSerializer,
    FilterShortSerializer
)


class FilterCategoryViewSet(ListModelMixin,
                            GenericViewSet):
    """
    Viewset class that provides `list()` action for Filter Category.
    """
    queryset = FilterCategory.objects.all()
    serializer_class = FilterCategorySerializer
    permission_classes = []


class FilterViewSet(ModelViewSet):
    """
    Viewset class that provides CRUD actions for Filter.
    """
    queryset = Filter.objects.none()
    serializer_class = FilterSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_serializer_class(self):
        """
        Returns serializer class depending on action method
        """

        if self.action == 'list':
            return FilterShortSerializer

        return FilterSerializer

    def get_queryset(self):
        """
        Returns queryset only with current user filters
        """

        user = self.request.user
        return Filter.objects.filter(owner_id=user.id).all()
