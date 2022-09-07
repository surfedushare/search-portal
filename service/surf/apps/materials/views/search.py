import logging

from django.apps import apps
from django.db.models import F, QuerySet
from django.shortcuts import Http404

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny

from surf.vendor.search.api import SearchApiClient
from surf.apps.core.schema import SearchSchema
from surf.apps.filters.serializers import MpttFilterItemSerializer
from surf.apps.materials.models import Material, SharedResourceCounter, RESOURCE_TYPE_MATERIAL
from surf.apps.materials.serializers import (
    SearchSerializer,
    KeywordsRequestSerializer,
    MaterialsRequestSerializer,
    MaterialShortSerializer,
    SharedResourceCounterSerializer
)
from surf.apps.materials.utils import (
    add_extra_parameters_to_materials,
    get_material_details_by_id,
    add_search_query_to_log
)


logger = logging.getLogger(__name__)
filters_app = apps.get_app_config("filters")


class MaterialSearchAPIView(CreateAPIView):
    """
    The main search endpoint.
    Specify the search query in the ``search_text`` property of the body to do a simple search.
    All other properties are optional and are described below

    ## Request body

    Apart from search_text you can specify the following properties in the body of the request:

    **page_size**: Number of results to return per page.

    **page**: A page number within the paginated result set.

    **ordering**: The external_id of a filter category to order results by (for instance: "publisher_date").
    This will ignore relevance of results and order by the specified property.
    By default ordering is ascending.
    If you specify the minus sign (for instance: "-publisher_date") the ordering will be descending.

    **filters**: Filters consist of an array of objects that specify an external_id and an items property.
    The external_id should be the value of a "field" filter category (for instance: "technical_type").
    See the filter categories endpoint described below for more details on filter categories.
    Next to the external_id you should specify an array under the items property.
    Elements in this array should only consist of values from category filter objects (for instance: "video").

    Filters under the same "field" filter category will function as an OR filter.
    While multiple filter category items across "field" filter categories function as AND filters.

    ## Response body

    **results**: An array containing the search results.

    **filter_categories**: An array with all filter categories.
    The frequency of the filter categories will indicate how many results match the filter category.

    **records_total**: Count of all available results

    **page_size**: Number of results to return per page.

    **page**: The current page number.

    """
    serializer_class = SearchSerializer
    permission_classes = (AllowAny,)
    schema = SearchSchema()

    def post(self, request, *args, **kwargs):
        # validate request parameters and prepare search
        serializer = SearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        data["drilldown_names"] = filters_app.metadata.get_filter_field_names()

        client = SearchApiClient()

        res = client.search(**data)
        records = res["records"]
        records = add_extra_parameters_to_materials(filters_app.metadata, records)

        filter_categories = MpttFilterItemSerializer(
            filters_app.metadata.tree,
            many=True,
            context={'drilldowns': res["drilldowns"]}
        )

        if data['page'] == 1 and data["search_text"]:
            add_search_query_to_log(res["recordcount"], data["search_text"], data["filters"])

        rv = dict(records=records,
                  records_total=res["recordcount"],
                  filter_categories=filter_categories.data,
                  page=data["page"],
                  page_size=data["page_size"],
                  did_you_mean=res["did_you_mean"])
        return Response(rv)


class KeywordsAPIView(ListAPIView):
    """
    This endpoint returns suggestions about what a user may be typing.
    Call this endpoint when a user is typing a search and display the results (for instance below the search bar).

    This endpoint only completes queries that are at least 4 characters.
    """

    serializer_class = KeywordsRequestSerializer
    permission_classes = (AllowAny,)
    schema = SearchSchema()
    queryset = QuerySet()
    pagination_class = None
    filter_backends = []

    def get(self, request, *args, **kwargs):
        # validate request parameters
        serializer = KeywordsRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        client = SearchApiClient()

        res = client.autocomplete(**data)
        return Response(res)


_MATERIALS_COUNT_IN_OVERVIEW = 4


class MaterialAPIView(APIView):
    """
    View class that provides retrieving Material by its edurep id (external_id)
    or retrieving overview of materials.
    If external_id exists in request data then `get()` method returns
    material by external_id, otherwise it returns overview of materials.
    """

    permission_classes = []

    def get(self, request, *args, **kwargs):
        # validate request parameters
        serializer = MaterialsRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        # default is false in the serializer
        count_view = data["count_view"]
        if "external_id" in kwargs:
            return self.get_material(request,
                                     kwargs["external_id"],
                                     count_view=count_view,
                                     shared=data.get("shared"))

        if "external_id" in data:
            res = _get_material_by_external_id(request,
                                               data["external_id"],
                                               shared=data.get("shared"))

        else:
            # return overview of newest Materials
            client = SearchApiClient()
            res = client.search('', ordering="-publisher_date", page_size=_MATERIALS_COUNT_IN_OVERVIEW)
            res = add_extra_parameters_to_materials(filters_app.metadata,
                                                    res["records"])
        return Response(res)

    @staticmethod
    def get_material(request, external_id, count_view, shared=None):
        """
        Returns the list of materials by external id
        :param request: request instance
        :param external_id: external id of material
        :param shared: share type of material
        :param count_view: should the view be counted in the statistics?
        :return:
        """
        res = _get_material_by_external_id(request, external_id, shared=shared, count_view=count_view)

        if not res:
            raise Http404()

        return Response(res[0])


def _get_material_by_external_id(request, external_id, shared=None, count_view=False):
    """
    Get Materials by edured id and register unique view of materials
    :param request:
    :param external_id: edured id of material
    :param shared: share type of material
    :return: list of materials
    """

    material, created = Material.objects.get_or_create(external_id=external_id)
    if created:
        material.sync_info()
    # increase unique view counter
    if count_view:
        material.view_count = F('view_count') + 1
        material.save()

    if shared:
        # increase share counter
        counter_key = SharedResourceCounter.create_counter_key(
            RESOURCE_TYPE_MATERIAL,
            external_id,
            share_type=shared)

        SharedResourceCounter.increase_counter(counter_key, extra=shared)

    rv = get_material_details_by_id(external_id)
    rv = add_extra_parameters_to_materials(filters_app.metadata, rv)
    rv = _add_share_counters_to_materials(rv)
    return rv


def _add_share_counters_to_materials(materials):
    """
    Add share counter values for materials.
    :param materials: array of materials
    :return: updated array of materials
    """
    for m in materials:
        key = SharedResourceCounter.create_counter_key(RESOURCE_TYPE_MATERIAL, m["external_id"])
        qs = SharedResourceCounter.objects.filter(counter_key__contains=key)
        m["sharing_counters"] = SharedResourceCounterSerializer(many=True).to_representation(qs.all())
    return materials


class MaterialSetAPIView(APIView):

    def get(self, request, *args, **kwargs):
        serializer = MaterialShortSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        results = _get_material_by_external_id(request, data['external_id'])
        parts = results[0]['has_parts']

        client = SearchApiClient()
        api_response = client.get_materials_by_id(parts, page_size=100)
        return Response(api_response)
