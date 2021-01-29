"""
This module contains implementation of REST API views for materials app.
"""

import json
import logging

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Count, F, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (
    ModelViewSet
)

from surf.apps.communities.models import Team, Community
from surf.apps.filters.models import MpttFilterItem
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
    SearchRequestSerializer,
    KeywordsRequestSerializer,
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
    add_material_themes,
    add_material_disciplines,
    add_search_query_to_elastic_index
)
from surf.vendor.search.choices import (
    AUTHOR_FIELD_ID,
    PUBLISHER_FIELD_ID
)
from surf.vendor.search.choices import DISCIPLINE_CUSTOM_THEME
from surf.vendor.elasticsearch.api import ElasticSearchApiClient


logger = logging.getLogger(__name__)


def portal_material(request, *args, **kwargs):
    material = _get_material_by_external_id(request, kwargs["external_id"])
    if material:
        return render(request, "portal/index.html", {
            'meta_og_title': material[0]["title"],
            'meta_og_description': material[0]["description"]
        })

    return portal_single_page_application(request, args)


def portal_single_page_application(request, *args):
    return render(request, "portal/index.html", {
        'meta_og_title': "SURF | edusources",
        'meta_og_description': "Edusources"
    })


class MaterialSearchAPIView(APIView):
    """
    View class that provides search action for Material by filters, author
    lookup text.
    """

    permission_classes = []

    @staticmethod
    def parse_theme_drilldowns(discipline_items):
        fields = dict()
        for item in discipline_items:
            item_id = item["external_id"]
            theme_ids = DISCIPLINE_CUSTOM_THEME.get(item_id)
            if not theme_ids:
                theme_ids = ["Unknown"]
            for f_id in theme_ids:
                fields[f_id] = fields.get(f_id, 0) + int(item["count"])

        fields = sorted(fields.items(), key=lambda kv: kv[1], reverse=True)
        return [dict(external_id=k, count=v) for k, v in fields]

    def post(self, request, *args, **kwargs):
        # validate request parameters
        serializer = SearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        filters = data.get("filters", [])
        # add additional filter by Author
        # if input data contains `author` parameter
        author = data.pop("author", None)
        if author:
            filters.append(dict(external_id=AUTHOR_FIELD_ID, items=[author]))

        publisher = data.pop("publisher", None)
        if publisher:
            filters.append(dict(external_id=PUBLISHER_FIELD_ID, items=[publisher]))

        data["filters"] = filters

        return_records = data.pop("return_records", None)
        return_filters = data.pop("return_filters", None)

        if not return_records:
            data["page_size"] = 0

        if return_filters:
            data["drilldown_names"] = [
                mptt_filter.external_id for mptt_filter in MpttFilterItem.objects.filter(parent=None)
            ]

        elastic = ElasticSearchApiClient()

        res = elastic.search(**data)
        records = add_extra_parameters_to_materials(request.user, res["records"])

        if return_filters and "lom.classification.obk.discipline.id" in data["drilldown_names"]:
            discipline_items = next(
                drilldown["items"]
                for drilldown in res["drilldowns"] if drilldown["external_id"] == "lom.classification.obk.discipline.id"
            )
            res["drilldowns"].append({
                "external_id": "custom_theme.id",
                "items": self.parse_theme_drilldowns(discipline_items)
            })

        drill_down_dict = {item['external_id']: item for item in res["drilldowns"]}
        drill_down_flat = {}
        for external_id, drilldown in drill_down_dict.items():
            if drilldown.get('count', None):
                drill_down_flat.update({external_id: drilldown})
            if drilldown['items']:
                for el in drilldown['items']:
                    drill_down_flat.update({el['external_id']: el})

        filter_category_tree = MpttFilterItem.objects.select_related("title_translations").get_cached_trees()
        filter_categories = MpttFilterItemSerializer(
            filter_category_tree,
            many=True,
            context={'search_counts': drill_down_flat}
        )

        if data['page'] == 1 and data["search_text"]:
            add_search_query_to_elastic_index(res["recordcount"], data["search_text"], data["filters"])

        rv = dict(records=records,
                  records_total=res["recordcount"],
                  filters=res["drilldowns"],
                  filter_categories=filter_categories.data,
                  page=data["page"],
                  page_size=data["page_size"],
                  did_you_mean=res["did_you_mean"])
        return Response(rv)


class KeywordsAPIView(APIView):
    """
    View class that provides search of keywords by text.
    """

    permission_classes = []

    def get(self, request, *args, **kwargs):
        # validate request parameters
        serializer = KeywordsRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        elastic = ElasticSearchApiClient()

        res = elastic.autocomplete(**data)
        return Response(res)


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
                                 ordering="-lom.lifecycle.contribute.publisherdate",
                                 page_size=_MATERIALS_COUNT_IN_OVERVIEW)

            res = add_extra_parameters_to_materials(request.user,
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

    material, created = Material.objects.get_or_create(external_id=external_id, deleted_at__isnull=True)
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
    rv = add_extra_parameters_to_materials(request.user, rv)
    rv = add_share_counters_to_materials(rv)
    return rv


class MaterialRatingAPIView(APIView):

    def post(self, request, *args, **kwargs):
        params = request.data.get('params')
        external_id = params['external_id']
        star_rating = params['star_rating']
        material_object = Material.objects.get(external_id=external_id, deleted_at__isnull=True)
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
        material_object = Material.objects.get(external_id=external_id, deleted_at__isnull=True)
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
        .annotate(community_cnt=Count('communities', filter=Q(deleted_at__isnull=True)))
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
            ids = [m.external_id for m in instance.materials.order_by("id").filter(deleted_at__isnull=True)]

            rv = dict(records=[],
                      records_total=0,
                      filters=[],
                      page=data["page"],
                      page_size=data["page_size"])

            if ids:
                elastic = ElasticSearchApiClient()

                res = elastic.get_materials_by_id(ids, 1, len(ids))
                records = res.get("records", [])
                records = add_extra_parameters_to_materials(request.user, records)

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

            serializer.is_valid(raise_exception=True)
            data.append(serializer.validated_data)

        if request.method == "POST":
            self._add_materials(instance, data)

        elif request.method == "DELETE":
            self._delete_materials(instance, data)

        res = MaterialShortSerializer(many=True).to_representation(
            instance.materials.filter(deleted_at__isnull=True)
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

            keywords = details[0].get("keywords")
            if keywords:
                keywords = json.dumps(keywords)

            m, _ = Material.objects.update_or_create(
                external_id=m_external_id, deleted_at__isnull=True,
                defaults=dict(material_url=details[0].get("url"),
                              title=details[0].get("title"),
                              description=details[0].get("description"),
                              keywords=keywords))

            add_material_themes(m, details[0].get("themes", []))
            add_material_disciplines(m, details[0].get("disciplines", []))
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
        parts = results[0]['has_part']

        api_client = ElasticSearchApiClient()
        api_response = api_client.get_materials_by_id(parts, page_size=100)
        return Response(api_response)
