from django.db.models import Q

from rest_framework.viewsets import GenericViewSet

from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin
)

from rest_framework.decorators import action
from rest_framework.response import Response

from surf.apps.filters.models import FilterCategoryItem
from surf.apps.themes.serializers import ThemeSerializer
from surf.vendor.edurep.xml_endpoint.v1_2.api import CUSTOM_THEME_FIELD_ID


class ThemeViewSet(ListModelMixin,
                   RetrieveModelMixin,
                   GenericViewSet):
    """
    View class that provides `GET` method for Themes.
    """

    queryset = FilterCategoryItem.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = []

    def get_queryset(self):
        return FilterCategoryItem.objects.filter(
            category__edurep_field_id=CUSTOM_THEME_FIELD_ID
        ).all()
