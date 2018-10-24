from rest_framework.views import APIView
from rest_framework import exceptions

from rest_framework.response import Response

from surf.apps.filters.models import FilterCategory

from surf.apps.materials.serializers import (
    SearchRequestSerializer,
    KeywordsRequestSerializer,
    MaterialsRequestSerializer
)

from surf.vendor.edurep.xml_endpoint.v1_2.api import (
    XmlEndpointApiClient,
    AUTHOR_FIELD_ID,
    PUBLISHER_FIELD_ID
)


class MaterialSearchAPIView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = SearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)

        author = data.pop("author", None)
        if author:
            filters = data.get("filters", [])
            filters.append(dict(external_id=AUTHOR_FIELD_ID, items=[author]))
            # filters.append(dict(external_id=PUBLISHER_FIELD_ID,
            #                     items=[author]))
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


def _get_filter_categories():
    return ["{}:{}".format(f.edurep_field_id, f.max_item_count)
            for f in FilterCategory.objects.all()]


class KeywordsAPIView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        serializer = KeywordsRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)

        ac = XmlEndpointApiClient()
        res = ac.autocomplete(**data)
        return Response(res)


class MaterialAPIView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        serializer = MaterialsRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)

        if "external_id" in data:
            ac = XmlEndpointApiClient()
            res = ac.get_materials_by_id([data["external_id"]])
            res = res.get("records", [])
        else:
            # TODO to be implemented
            res = []
        return Response(res)
