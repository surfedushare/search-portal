from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import exceptions

from rest_framework import (
    mixins,
    viewsets,
    permissions
)

from rest_framework.response import Response

from rest_framework.decorators import (
    detail_route,
    list_route
)

from surf.apps.filters.utils import check_and_update_filters
from surf.apps.filters.models import FilterCategory

from surf.vendor.edurep.xml_endpoint.v1_2.api import XmlEndpointApiClient


class MaterialSearchAPIView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        # TODO validation of page, page_size
        d = request.data
        query = d.get("query", "")
        page = d.get("page", 1)
        page_size = d.get("page_size", 5)
        ordering = d.get("ordering")
        filters = d.get("filters", dict())

        ac = XmlEndpointApiClient()
        res = ac.search(query=query)

        # f_params = dict()

        # for f, v in filters.items():
        #     for p in v:
        #         f_params.setdefault(f, []).append(p)
        #
        # return Response(dict(query=query, page=page, page_size=page_size,
        #                      filters=f_params))
        return Response(res)


class MaterialFiltersAPIView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        # TODO
        d = request.data
        query = d.get("query", "")
        filters = d.get("filters", dict())

        ac = XmlEndpointApiClient()
        res = ac.drilldowns(_get_filter_categories(), query=query)

        # check_and_update_filters()
        #
        # f_params = dict()
        #
        # for f, v in filters.items():
        #     for p in v:
        #         f_params.setdefault(f, []).append(p)

        # return Response(dict(query=query, filters=f_params))
        return Response(res)


def _get_filter_categories():
    return ["{}:{}".format(f.edurep_field_id, f.max_item_count)
            for f in FilterCategory.objects.all()]


class KeywordsAPIView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        d = request.GET
        query = d.get("query", "")
        if not query:
            exceptions.ValidationError("Empty query")

        ac = XmlEndpointApiClient()
        res = ac.autocomplete(query)
        return Response(res)
