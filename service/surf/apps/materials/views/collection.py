import logging

from django.apps import apps
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import get_object_or_404, Http404
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed, MethodNotAllowed
from rest_framework.viewsets import ModelViewSet

from surf.vendor.search.api import SearchApiClient
from surf.apps.communities.models import Team, Community
from surf.apps.materials.models import (
    Collection,
    Material,
    CollectionMaterial,
    SharedResourceCounter,
    RESOURCE_TYPE_COLLECTION
)
from surf.apps.materials.serializers import (
    CollectionSerializer,
    CollectionMaterialsRequestSerializer,
    MaterialShortSerializer,
    CollectionMaterialPositionSerializer,
)
from surf.apps.materials.utils import add_extra_parameters_to_materials, get_material_details_by_id
from surf.apps.materials.filters import CollectionFilter


logger = logging.getLogger(__name__)
filters_app = apps.get_app_config("filters")


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
                client = SearchApiClient()

                res = client.get_materials_by_id(ids, 1, len(ids))
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
