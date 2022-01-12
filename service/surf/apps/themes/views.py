from django.shortcuts import Http404
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
    lookup_url_kwarg = "slug"

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.filter(nl_slug=self.kwargs["slug"]).first()
        if not object:
            obj = queryset.filter(en_slug=self.kwargs["slug"]).first()
        if obj is None:
            raise Http404()
        self.check_object_permissions(self.request, obj)
        return obj
