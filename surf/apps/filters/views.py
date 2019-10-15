"""
This module contains implementation of REST API views for filters app.
"""

from types import SimpleNamespace

from rest_framework import status, generics
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet
)

from surf.apps.filters.models import (
    Filter,
    MpttFilterItem
)
from surf.apps.filters.serializers import (
    FilterSerializer,
    FilterShortSerializer,
    MpttFilterItemSerializer,
)
from surf.apps.materials.views import MaterialSearchAPIView


class FilterCategoryViewSet(ListModelMixin, GenericViewSet):
    """
    Viewset class that provides `list()` action for Filter Category.
    """
    serializer_class = MpttFilterItemSerializer
    permission_classes = []

    @classmethod
    def _update_item_counts_for_node(cls, input_node, item_count_dict):
        if input_node['external_id'] in item_count_dict.keys():
            input_node['item_count'] = item_count_dict[input_node['external_id']]
        elif input_node['name'] in item_count_dict.keys():
            input_node['item_count'] = item_count_dict[input_node['name']]
        if input_node['children'] is not None:
            for child_node in input_node['children']:
                cls._update_item_counts_for_node(child_node, item_count_dict)

    def remove_zero_counts(self, input_node):
        if not input_node['external_id'] == "lom.general.language":
            for child in input_node['children']:
                self.remove_zero_counts(child)
            input_node['children'] = [child for child in input_node['children']
                                      if child['item_count'] > 0
                                      or len(child['children']) > 0]

    def list(self, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        item_counts = self.get_counts(*args)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            for node in serializer.data:
                self._update_item_counts_for_node(node, item_counts)
                self.remove_zero_counts(node)

            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        for node in serializer.data:
            self._update_item_counts_for_node(node, item_counts)
            self.remove_zero_counts(node)

        return Response(serializer.data, status.HTTP_200_OK)

    def get_queryset(self):
        return MpttFilterItem.objects.select_related("title_translations").get_cached_trees()

    def get_counts(self, request, **kwargs):
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
        return external_id_count


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


class MpttFilterItems(generics.GenericAPIView):
    serializer_class = MpttFilterItemSerializer


