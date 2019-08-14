"""
This module contains implementation of REST API views for filters app.
"""

from types import SimpleNamespace

from django.shortcuts import render
from rest_framework import views
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet
)

from surf.apps.filters.models import (
    FilterCategory,
    Filter,
    MpttFilterItem
)
from surf.apps.filters.serializers import (
    FilterCategorySerializer,
    FilterSerializer,
    FilterShortSerializer
)
from surf.apps.materials.views import MaterialSearchAPIView


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


class MpttFilterItems(views.APIView):

    def get(self, request, **kwargs):
        filter_items = MpttFilterItem.objects.all()

        # do an empty TODO (should it be empty _always_?)
        # query to edurep to get the counts of the filter items
        filters = []
        if 'filters' in request.data.keys():
            filters = request.data['filters']
        base_request = SimpleNamespace(**{'data': {'search_text': [], 'filters': filters}, 'user': None})
        viewer = MaterialSearchAPIView()
        response = viewer.post(request=base_request)

        # extract the filter counts from the response
        external_id_count = {}
        for item in response.data['filters']:
            category_count = 0
            for sub_item in item['items']:
                category_count += sub_item['count']
                external_id_count[sub_item['external_id']] = sub_item['count']
            external_id_count[item['external_id']] = category_count

        # add the filter counts to the filter items
        for filter_item in filter_items:
            if filter_item.external_id in external_id_count.keys():
                filter_item.item_count = external_id_count[filter_item.external_id]

        # most likely don't filter empty items here in the futurue TODO
        filter_items = [filter_item for filter_item in filter_items if filter_item.item_count > 0]
        return render(request, "MpttFilterItems.html", {'MpttFilterItems': filter_items})
