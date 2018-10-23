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

from surf.apps.materials import serializers

from surf.vendor.edurep.xml_endpoint.v1_2.api import (
    XmlEndpointApiClient,
    AUTHOR_FIELD_ID
)


class MaterialSearchAPIView(APIView):
    permission_classes = []

    serializer_class = serializers.SearchRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)

        author = data.pop("author", None)
        if author:
            filters = data.get("filters", [])
            filters.append(dict(id=AUTHOR_FIELD_ID, items=[author]))
            data["filters"] = filters

        return_records = data.pop("return_records", None)
        return_filters = data.pop("return_filters", None)

        if not return_records:
            data["page_size"] = 0

        if return_filters:
            data["drilldown_names"] = _get_filter_categories()

        ac = XmlEndpointApiClient()
        res = ac.search(**data)

        rv = dict(records=res["records"],
                  records_total=res["recordcount"],
                  filters=res["drilldowns"],
                  page=data["page"],
                  page_size=data["page_size"])
        return Response(rv)


class MaterialFiltersAPIView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        # TODO to be implemented
        d = request.data
        queries = d.get("query", [])
        filters = d.get("filters", dict())

        ac = XmlEndpointApiClient()
        res = ac.drilldowns(_get_filter_categories(), queries=queries)

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
