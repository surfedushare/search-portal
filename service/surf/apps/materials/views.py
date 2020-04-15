"""
This module contains implementation of REST API views for materials app.
"""

import json
import logging

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Count
from django.db.models import F
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (
    ModelViewSet
)

from surf.apps.communities.models import Team, Community
from surf.apps.filters.models import MpttFilterItem
from surf.apps.filters.utils import IGNORED_FIELDS, add_default_material_filters
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
    SharedResourceCounterSerializer
)
from surf.apps.materials.utils import (
    add_extra_parameters_to_materials,
    get_material_details_by_id,
    add_material_themes,
    add_material_disciplines
)
from surf.vendor.edurep.xml_endpoint.v1_2.api import (
    AUTHOR_FIELD_ID
)
from surf.vendor.search.choices import DISCIPLINE_CUSTOM_THEME
from surf.vendor.search.searchselector import get_search_client

logger = logging.getLogger(__name__)


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


class MaterialSearchAPIView(APIView):
    """
    View class that provides search action for Material by filters, author
    lookup text.
    """

    permission_classes = []

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

        # add default filters to search materials
        filters = add_default_material_filters(filters)

        data["filters"] = filters

        return_records = data.pop("return_records", None)
        return_filters = data.pop("return_filters", None)

        if not return_records:
            data["page_size"] = 0

        if return_filters:
            data["drilldown_names"] = _get_filter_categories()

        # This is an ugly hack where we make the "vaktherapie" demo work.
        # We should configure ES to use decompound filters or similar.
        # However there are some blockers for this and to keep moving forward we decompound "vaktherapie" hardcoded.
        # That way the demo to clients works as expected while we don't have to wait with ES rollout.
        try:
            index = [search.lower() for search in data["search_text"]].index("vaktherapie")
            data["search_text"][index] = "vaktherapie vak therapie"
        except ValueError:
            pass

        ac = get_search_client()

        res = ac.search(**data)
        records = add_extra_parameters_to_materials(request.user, res["records"])

        if return_filters and "lom.classification.obk.discipline.id" in data["drilldown_names"]:
            discipline_items = next(
                drilldown["items"]
                for drilldown in res["drilldowns"] if drilldown["external_id"] == "lom.classification.obk.discipline.id"
            )
            res["drilldowns"].append({
                "external_id": "custom_theme.id",
                "items": parse_theme_drilldowns(discipline_items)
            })

        rv = dict(records=records,
                  records_total=res["recordcount"],
                  filters=res["drilldowns"],
                  page=data["page"],
                  page_size=data["page_size"])
        return Response(rv)


def _get_filter_categories():
    """
    Make list of filter categories in format "edurep_field_id:item_count"
    :return: list of "edurep_field_id:item_count"
    """
    return [f.external_id for f in MpttFilterItem.objects.all()
            if f.external_id not in IGNORED_FIELDS
            and f.level == 0]


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

        ac = get_search_client()

        res = ac.autocomplete(**data)
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
            ac = get_search_client()

            # add default filters to search materials
            filters = add_default_material_filters()

            res = ac.search([],
                            # sort by newest items first
                            ordering="-lom.lifecycle.contribute.publisherdate",
                            filters=filters,
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
            raise Http404('No materials matches the given query.')

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
    rv = add_extra_parameters_to_materials(request.user, rv)
    rv = add_share_counters_to_materials(rv)
    return rv


class MaterialRatingAPIView(APIView):
    # I don't think we really need the get, but the frontend uses it so I'll leave it be
    def get(self, request, *args, **kwargs):
        external_id = request.GET['external_id']
        return Response(f"External id {external_id} is valid")

    def post(self, request, *args, **kwargs):
        params = request.data.get('params')
        external_id = params['external_id']
        star_rating = params['star_rating']
        material_object = Material.objects.get(external_id=external_id)
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
    # I don't think we really need the get, but the frontend uses it so I'll leave it be
    def get(self, request, *args, **kwargs):
        external_id = request.GET['external_id']
        return Response(f"External id {external_id} is valid")

    def post(self, request, *args, **kwargs):
        params = request.data.get('params')
        external_id = params['external_id']
        material_object = Material.objects.get(external_id=external_id)
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
            raise Http404(f"Collection {collection_instance} does not contain a material with "
                          f"external id {external_id}, cannot promote or demote")

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

    queryset = Collection.objects.filter(deleted_at=None)
    serializer_class = CollectionSerializer
    filter_class = CollectionFilter
    permission_classes = []

    def get_queryset(self):
        return Collection.objects.annotate(community_cnt=Count('communities')).filter(community_cnt__gt=0)

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
            ids = [m.external_id for m in instance.materials.order_by("id").all()]

            featured = CollectionMaterial.objects.filter(collection=instance, featured=True)
            featured_ids = [m.material.external_id for m in featured]

            rv = dict(records=[],
                      records_total=0,
                      filters=[],
                      page=data["page"],
                      page_size=data["page_size"])

            if ids:
                ac = get_search_client()

                res = ac.get_materials_by_id(ids, **data)
                records = res.get("records", [])
                records = add_extra_parameters_to_materials(request.user, records)
                for record in records:
                    if record['external_id'] in featured_ids:
                        record['featured'] = True
                    else:
                        record['featured'] = False

                rv["records"] = records
                rv["records_total"] = res["recordcount"]

            return Response(rv)

        data = []
        for d in request.data:
            # validate request parameters
            serializer = MaterialShortSerializer(data=d)
            serializer.is_valid(raise_exception=True)
            data.append(serializer.validated_data)

        if request.method == "POST":
            self._add_materials(instance, data)

        elif request.method == "DELETE":
            self._delete_materials(instance, data)

        res = MaterialShortSerializer(many=True).to_representation(instance.materials.all())
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

            details = get_material_details_by_id(m_external_id)
            if not details:
                continue

            keywords =details[0].get("keywords")
            if keywords:
                keywords = json.dumps(keywords)

            m, _ = Material.objects.update_or_create(
                external_id=m_external_id,
                defaults=dict(material_url=details[0].get("url"),
                              title=details[0].get("title"),
                              description=details[0].get("description"),
                              keywords=keywords))

            add_material_themes(m, details[0].get("themes", []))
            add_material_disciplines(m, details[0].get("disciplines", []))
            CollectionMaterial.objects.create(collection=instance, material=m)

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
            logger.debug(f"At least one team satisfies the requirement of be able to delete this collection.")
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
        key = SharedResourceCounter.create_counter_key(RESOURCE_TYPE_MATERIAL,m["external_id"])
        qs = SharedResourceCounter.objects.filter(counter_key__contains=key)
        m["sharing_counters"] = SharedResourceCounterSerializer(many=True).to_representation(qs.all())

    return materials
