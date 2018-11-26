from django.db.models import Count

from rest_framework.viewsets import GenericViewSet

from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin
)

from rest_framework.decorators import action
from rest_framework.response import Response

from surf.apps.themes.models import Theme
from surf.apps.materials.models import Material, Collection
from surf.apps.communities.models import Community
from surf.apps.themes.serializers import ThemeSerializer
from surf.apps.filters.serializers import FilterCategoryItemSerializer
from surf.apps.communities.serializers import CommunitySerializer
from surf.apps.materials.serializers import CollectionSerializer


_COLLECTIONS_COUNT_IN_OVERVIEW = 4


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
        """
        Returns disciplines related to the theme
        """

        instance = self.get_object()

        res = []
        if instance.disciplines.exists():
            res = FilterCategoryItemSerializer(many=True).to_representation(
                instance.disciplines.all())

        return Response(res)

    @action(methods=['get'], detail=True)
    def communities(self, request, pk=None, **kwargs):
        """
        Returns the communities related to the theme
        """

        instance = self.get_object()

        qs = Collection.objects.filter(materials__themes__id=instance.id)
        ids = qs.values_list('communities__id', flat=True)
        qs = Community.objects.filter(id__in=ids)

        context = self.get_serializer_context()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = CommunitySerializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        res = CommunitySerializer(
            many=True, context=context
        ).to_representation(
            qs.all()
        )
        return Response(res)

    @action(methods=['get'], detail=True, url_path="community-collections")
    def community_collections(self, request, pk=None, **kwargs):
        """
        Returns the overview of collections from communities
        related to the theme
        """

        instance = self.get_object()

        qs = Material.objects.filter(themes__id=instance.id)
        ids = qs.values_list('collections__id', flat=True)
        qs = Collection.objects.filter(id__in=ids, communities__isnull=False)
        qs = qs.annotate(community_cnt=Count('communities'))
        cs = qs.all()
        if qs.count() > _COLLECTIONS_COUNT_IN_OVERVIEW:
            cs = cs[:_COLLECTIONS_COUNT_IN_OVERVIEW]

        res = []
        if cs:
            res = CollectionSerializer(
                many=True,
                context=self.get_serializer_context()
            ).to_representation(cs)

        return Response(res)
