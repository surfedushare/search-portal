"""
This module contains implementation of REST API views for filters app.
"""
import time

from collections import OrderedDict
from types import SimpleNamespace

from django.shortcuts import render
from rest_framework import views, status, generics
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
    FilterShortSerializer,
    MpttFilterItemSerializer,
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


class MpttFilterItems(generics.GenericAPIView):
    serializer_class = MpttFilterItemSerializer
    queryset = MpttFilterItem.objects.get_cached_trees()

    def get(self, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        item_counts = self.get_counts(*args)
        serializer = self.get_serializer(queryset, many=True)

        def update_item_counts_for_node(input_node, item_count_dict):
            if input_node['external_id'] in item_count_dict.keys():
                input_node['item_count'] = item_count_dict[input_node['external_id']]
            if input_node['children'] is not None:
                for child_node in input_node['children']:
                    update_item_counts_for_node(child_node, item_count_dict)

        for node in serializer.data:
            update_item_counts_for_node(node, item_counts)
        return Response(serializer.data, status.HTTP_200_OK)

    def get_counts(self, request, **kwargs):
        filters = []
        if 'filters' in request.data.keys():
            filters = request.data['filters']
        #filters = [OrderedDict([('external_id', 'lom.classification.obk.discipline.id'), ('items', ['bc0217df-c38d-4c29-b87b-2c1c035c717f'])])]
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
