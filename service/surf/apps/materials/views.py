import logging

from django.conf import settings
from django.apps import apps
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Count, F, Q, QuerySet
from django.shortcuts import get_object_or_404, render, Http404
from django.views.decorators.gzip import gzip_page
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed, MethodNotAllowed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.viewsets import (
    ModelViewSet
)
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer

from surf.apps.communities.models import Team, Community
from surf.apps.filters.serializers import MpttFilterItemSerializer
from surf.apps.materials.filters import (
    CollectionFilter
)
from surf.apps.materials.models import (
    Collection,
    Material,
    CollectionMaterial,
    SharedResourceCounter,
    RESOURCE_TYPE_MATERIAL,
    RESOURCE_TYPE_COLLECTION
)
from surf.apps.materials.serializers import (
    SearchSerializer,
    KeywordsRequestSerializer,
    SimilaritySerializer,
    AuthorSuggestionSerializer,
    MaterialsRequestSerializer,
    CollectionSerializer,
    CollectionMaterialsRequestSerializer,
    MaterialShortSerializer,
    CollectionMaterialPositionSerializer,
    SharedResourceCounterSerializer
)
from surf.apps.materials.utils import (
    add_extra_parameters_to_materials,
    get_material_details_by_id,
    add_search_query_to_elastic_index
)
from surf.apps.locale.models import Locale
from surf.apps.core.schema import SearchSchema
from surf.vendor.elasticsearch.api import ElasticSearchApiClient


logger = logging.getLogger(__name__)
filters_app = apps.get_app_config("filters")


@gzip_page
def portal_material(request, *args, **kwargs):
    material = _get_material_by_external_id(request, kwargs["external_id"])
    if not material:
        raise Http404(f"Material not found: {kwargs['external_id']}")
    return render(request, "portal/index.html", {
        'meta_title': f"{material[0]['title']} | Edusources",
        'meta_description': material[0]["description"],
        'matomo_id': settings.MATOMO_ID
    })


@gzip_page
def portal_single_page_application(request, *args):
    site_description_translation = Locale.objects.filter(asset="meta-site-description").last()
    site_description = getattr(site_description_translation, request.LANGUAGE_CODE, "Edusources")
    filter_category_tree = filters_app.metadata.tree
    filter_categories = MpttFilterItemSerializer(
        filter_category_tree,
        many=True
    )
    return render(request, "portal/index.html", {
        'meta_title': "Edusources",
        'meta_description': site_description,
        'matomo_id': settings.MATOMO_ID,
        'filter_categories_json': JSONRenderer().render(filter_categories.data).decode("utf-8")
    })


@gzip_page
def portal_page_not_found(request, exception, template_name=None):
    site_description_translation = Locale.objects.filter(asset="meta-site-description").last()
    site_description = getattr(site_description_translation, request.LANGUAGE_CODE, "Edusources")
    return render(
        request,
        "portal/index.html",
        context={
            'meta_title': "Edusources",
            'meta_description': site_description,
            'matomo_id': settings.MATOMO_ID
        },
        status=404
    )


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

        elastic = ElasticSearchApiClient()

        res = elastic.search(**data)
        records = res["records"]
        records = add_extra_parameters_to_materials(filters_app.metadata, records)

        filter_categories = MpttFilterItemSerializer(
            filters_app.metadata.tree,
            many=True,
            context={'drilldowns': res["drilldowns"]}
        )

        if data['page'] == 1 and data["search_text"]:
            add_search_query_to_elastic_index(res["recordcount"], data["search_text"], data["filters"])

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

        elastic = ElasticSearchApiClient()

        res = elastic.autocomplete(**data)
        return Response(res)


class SimilarityAPIView(RetrieveAPIView):
    """
    This endpoint returns similar documents as the input document.
    These similar documents can be offered as suggestions to look at for the user.
    """

    serializer_class = SimilaritySerializer
    permission_classes = (AllowAny,)
    schema = SearchSchema()
    pagination_class = None
    filter_backends = []

    def get_object(self):
        serializer = self.get_serializer(data=self.request.GET)
        serializer.is_valid(raise_exception=True)
        external_id = serializer.validated_data["external_id"]
        language = serializer.validated_data["language"]
        elastic = ElasticSearchApiClient()
        result = elastic.more_like_this(external_id, language)
        result["results"] = add_extra_parameters_to_materials(filters_app.metadata, result["results"])
        return result


class AuthorSuggestionsAPIView(RetrieveAPIView):
    """
    This endpoint returns documents where the name of the author appears in the text or metadata,
    but is not set as author in the authors field.
    These documents can be offered to authors as suggestions for more content from their hand.
    """

    serializer_class = AuthorSuggestionSerializer
    permission_classes = (AllowAny,)
    schema = SearchSchema()
    pagination_class = None
    filter_backends = []

    def get_object(self):
        serializer = self.get_serializer(data=self.request.GET)
        serializer.is_valid(raise_exception=True)
        author_name = serializer.validated_data["author_name"]
        elastic = ElasticSearchApiClient()
        result = elastic.author_suggestions(author_name)
        result["results"] = add_extra_parameters_to_materials(filters_app.metadata, result["results"])
        return result


_MATERIALS_COUNT_IN_OVERVIEW = 4


class MaterialAPIView(APIView):
    """
    View class that provides retrieving Material by its edurep id (external_id)
    or retrieving overview of materials.
    If external_id is exist in request data then `get()` method returns
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
            elastic = ElasticSearchApiClient()

            res = elastic.search('',
                                 # sort by newest items first
                                 ordering="-publisher_date",
                                 page_size=_MATERIALS_COUNT_IN_OVERVIEW)

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
    rv = add_share_counters_to_materials(rv)
    return rv


class MaterialRatingAPIView(APIView):

    def post(self, request, *args, **kwargs):
        params = request.data.get('params')
        external_id = params['external_id']
        star_rating = params['star_rating']
        material_object = Material.objects.get(external_id=external_id, deleted_at=None)
        if star_rating == 1:
            material_object.star_1 = F('star_1') + 1
        if star_rating == 2:
            material_object.star_2 = F('star_2') + 1
        if star_rating == 3:
            material_object.star_3 = F('star_3') + 1
        if star_rating == 4:
            material_object.star_4 = F('star_4') + 1
        if star_rating == 5:
            material_object.star_5 = F('star_5') + 1
        material_object.save()
        material_object.refresh_from_db()
        return Response(material_object.get_avg_star_rating())


class MaterialApplaudAPIView(APIView):

    def post(self, request, *args, **kwargs):
        params = request.data.get('params')
        external_id = params['external_id']
        material_object = Material.objects.get(external_id=external_id, deleted_at=None)
        material_object.applaud_count = F('applaud_count') + 1
        material_object.save()
        material_object.refresh_from_db()
        return Response(material_object.applaud_count)


class CollectionMaterialPromotionAPIView(APIView):

    def post(self, request, *args, **kwargs):
        # only active and authorized users can promote materials in the collection
        collection_instance = Collection.objects.get(id=kwargs['collection_id'])

        # check whether the material is actually in the collection
        external_id = kwargs['external_id']
        collection_materials = CollectionMaterial.objects.filter(
            collection=collection_instance, material__external_id=external_id)
        if not collection_materials:
            raise Http404()

        # The material should only be in the collection once
        assert len(collection_materials) == 1, f"Material with id {external_id} is in collection " \
                                               f"{collection_instance} multiple times."
        collection_material = collection_materials[0]
        # promote or demote the material
        collection_material.featured = not collection_material.featured
        collection_material.save()

        return Response(serializers.serialize('json', [collection_material]))


class CollectionViewSet(ModelViewSet):
    """
    View class that provides CRUD methods for Collection and `get`, `add`
    and `delete` methods for its materials.
    """

    queryset = Collection.objects \
        .filter(deleted_at=None) \
        .annotate(community_cnt=Count('communities', filter=Q(deleted_at=None)))
    serializer_class = CollectionSerializer
    filter_class = CollectionFilter
    permission_classes = []

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        shared = request.GET.get("shared")
        if shared:
            # increase sharing counter
            counter_key = SharedResourceCounter.create_counter_key(
                RESOURCE_TYPE_COLLECTION,
                str(instance.id),
                share_type=shared)

            SharedResourceCounter.increase_counter(counter_key, extra=shared)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        if self.request.method != 'GET':
            check_access_to_collection(self.request.user, obj)
        return obj

    @action(methods=['get', 'post', 'delete'], detail=True)
    def materials(self, request, pk=None, **kwargs):
        instance = self.get_object()

        if request.method == "GET":
            # validate request parameters
            serializer = CollectionMaterialsRequestSerializer(data=request.GET)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            ids = [m.external_id for m in instance.materials.order_by("id").filter()]

            rv = dict(records=[],
                      records_total=0,
                      filters=[],
                      page=data["page"],
                      page_size=data["page_size"])

            if ids:
                elastic = ElasticSearchApiClient()

                res = elastic.get_materials_by_id(ids, 1, len(ids))
                records = res.get("records", [])
                records = add_extra_parameters_to_materials(filters_app.metadata, records)

                collection_materials = CollectionMaterial.objects.filter(
                    collection=instance, material__external_id__in=[r['external_id'] for r in records]
                )

                for collection_material in collection_materials:
                    record = next(r for r in records if r['external_id'] == collection_material.material.external_id)
                    record['featured'] = collection_material.featured
                    record['position'] = collection_material.position

                rv["records"] = records
                rv["records_total"] = res["recordcount"]

            return Response(rv)

        data = []
        for d in request.data:
            # validate request parameters
            if request.method == "POST":
                serializer = CollectionMaterialPositionSerializer(data=d)
            elif request.method == "DELETE":
                serializer = MaterialShortSerializer(data=d)
            else:
                raise MethodNotAllowed(request.method, detail="Method not supported")

            serializer.is_valid(raise_exception=True)
            data.append(serializer.validated_data)

        if request.method == "POST":
            self._add_materials(instance, data)

        elif request.method == "DELETE":
            self._delete_materials(instance, data)

        res = MaterialShortSerializer(many=True).to_representation(
            instance.materials.filter(deleted_at=None)
        )
        return Response(res)

    @staticmethod
    def _add_materials(instance, materials):
        """
        Add materials to collection
        :param instance: collection instance
        :param materials: added materials
        :return:
        """

        for material in materials:
            m_external_id = material["external_id"]
            m_position = material["position"]

            details = get_material_details_by_id(m_external_id)
            if not details:
                continue

            m, _ = Material.objects.update_or_create(external_id=m_external_id)
            CollectionMaterial.objects.create(collection=instance, material=m, position=m_position)

    @staticmethod
    def _delete_materials(instance, materials):
        """
        Delete materials from collection
        :param instance: collection instance
        :param materials: materials that should be removed from collection
        :return:
        """

        materials = [m["external_id"] for m in materials]
        materials = Material.objects.filter(external_id__in=materials).all()
        instance.materials.remove(*materials)


def check_access_to_collection(user, instance=None):
    """
    Check if user is active and owner of collection (if collection
    is not None)
    :param user: user
    :param instance: collection instance
    :return:
    """
    if not user or not user.is_authenticated:
        raise AuthenticationFailed()
    try:
        community = Community.objects.get(collections__in=[instance])
        Team.objects.get(community=community, user=user)
    except ObjectDoesNotExist as exc:
        raise AuthenticationFailed(f"User {user} is not a member of a community that has collection {instance}. "
                                   f"Error: \"{exc}\"")
    except MultipleObjectsReturned as exc:
        logger.warning(f"The collection {instance} is in multiple communities. Error:\"{exc}\"")
        communities = Community.objects.filter(collections__in=[instance])
        teams = Team.objects.filter(community__in=communities, user=user)
        if len(teams) > 0:
            logger.debug("At least one team satisfies the requirement of be able to delete this collection.")
        else:
            raise AuthenticationFailed(f"User {user} is not a member of any community with collection {instance}. "
                                       f"Error: \"{exc}\"")


def add_share_counters_to_materials(materials):
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

        api_client = ElasticSearchApiClient()
        api_response = api_client.get_materials_by_id(parts, page_size=100)
        return Response(api_response)
