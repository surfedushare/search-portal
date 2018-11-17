from django.db.models import Q

from rest_framework.viewsets import GenericViewSet

from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin
)

from rest_framework.decorators import action
from rest_framework.response import Response

from surf.apps.themes.models import Theme
from surf.apps.themes.serializers import ThemeSerializer
from surf.apps.filters.serializers import FilterCategoryItemSerializer


class ThemeViewSet(ListModelMixin,
                   RetrieveModelMixin,
                   GenericViewSet):
    """
    View class that provides `GET` method for Themes.
    """

    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = []
    lookup_field = 'filter_category_item__id'

    @action(methods=['get'], detail=True)
    def disciplines(self, request, pk=None, **kwargs):
        instance = self.get_object()

        res = []
        if instance.disciplines.exists():
            res = FilterCategoryItemSerializer(many=True).to_representation(
                instance.disciplines.all())

        return Response(res)
