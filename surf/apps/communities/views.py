"""
This module contains implementation of REST API views for communities app.
"""

import logging

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from surf.apps.communities.models import Community, Team, CommunityDetail
from surf.apps.communities.serializers import (
    CommunitySerializer,
    CommunityDisciplineSerializer,
    CommunityDetailSerializer)
from surf.apps.filters.models import MpttFilterItem
from surf.apps.materials.models import Collection
from surf.apps.materials.serializers import (
    CollectionSerializer,
    CollectionShortSerializer
)
from surf.apps.themes.models import Theme
from surf.apps.themes.serializers import ThemeSerializer

logger = logging.getLogger(__name__)


class CommunityViewSet(ListModelMixin,
                       RetrieveModelMixin,
                       UpdateModelMixin,
                       GenericViewSet):
    """
    View class that provides `GET` and `UPDATE` methods for Community.
    """

    queryset = Community.objects.filter(deleted_at=None)
    serializer_class = CommunitySerializer
    permission_classes = []

    def update(self, request, *args, **kwargs):
        # only active admins can update community
        #check_access_to_community(request.user, instance=self.get_object())
        return super().update(request, *args, **kwargs)

    @action(methods=['get', 'post', 'delete'], detail=True)
    def collections(self, request, pk=None, **kwargs):
        """
        Returns community collections
        """

        instance = self.get_object()

        qs = instance.collections
        if request.method in {"POST", "DELETE"}:
            # validate request parameters
            serializer = CollectionShortSerializer(many=True, data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.initial_data
            collection_ids = [d["id"] for d in data]
            check_access_to_community(request.user, instance=instance)
            if request.method == "POST":
                self._add_collections(instance, data)
                qs = qs.filter(id__in=collection_ids)

            elif request.method == "DELETE":
                self._delete_collections(instance, data)
                return Response()

        qs = qs.annotate(community_cnt=Count('communities'))

        if request.method == "GET":
            page = self.paginate_queryset(qs)
            if page is not None:
                serializer = CollectionSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        res = CollectionSerializer(many=True).to_representation(qs.all())
        return Response(res)

    @action(methods=['get'], detail=True)
    def themes(self, request, pk=None, **kwargs):
        """
        Returns themes related to community
        """

        instance = self.get_object()

        ids = instance.collections.values_list("materials__themes__id",
                                               flat=True)
        qs = Theme.objects.filter(id__in=ids)

        res = []
        if qs.exists():
            res = ThemeSerializer(many=True).to_representation(qs.all())

        return Response(res)

    @action(methods=['get'], detail=True)
    def disciplines(self, request, pk=None, **kwargs):
        """
        Returns disciplines related to collection materials
        """

        instance = self.get_object()

        ids = instance.collections.values_list("materials__disciplines__id",
                                               flat=True)
        qs = MpttFilterItem.objects.filter(id__in=ids)

        context = self.get_serializer_context()
        context["mptt_tree"] = MpttFilterItem.objects.get_cached_trees()

        res = CommunityDisciplineSerializer(
            many=True, context=context
        ).to_representation(
            qs.all()
        )

        return Response(res)

    @staticmethod
    def _add_collections(instance, collections):
        """
        Adds collections to community
        :param instance: community instance
        :param collections: added collections
        :return:
        """

        collections = [c["id"] for c in collections]
        collections = Collection.objects.filter(id__in=collections).all()
        instance.collections.add(*collections)

    @staticmethod
    def _delete_collections(instance, collections):
        """
        Deletes collections from community
        :param instance: community instance
        :param collections: collections that should be deleted
        :return:
        """
        collections = [c["id"] for c in collections]
        collections = Collection.objects.filter(id__in=collections).all()
        instance.collections.remove(*collections)


class CommunityDetailAPIView(APIView):
    def get(self, request, *args, **kwargs):
        language_code = kwargs['language_code'].upper()
        community_id = kwargs['community_id']

        try:
            detail_object = CommunityDetail.objects.get(community__id=community_id, language_code=language_code)
        except ObjectDoesNotExist:
            return Response(f"Community has no details for this language.")

        return Response(CommunityDetailSerializer(detail_object).data)

    def post(self, request, *args, **kwargs):
        language_code = kwargs['language_code'].upper()
        community_id = kwargs['community_id']
        community_object = Community.objects.get(id=community_id)
        check_access_to_community(request.user, community_object)
        detail_object, created = CommunityDetail.objects.get_or_create(community=community_object,
                                                                       language_code=language_code)
        for attr, value in request.data.items():
            if value is not None:
                setattr(detail_object, attr, value)
        detail_object.save()

        return Response(CommunityDetailSerializer(detail_object).data)


def check_access_to_community(user, instance=None):
    """
    Check if user is active and admin of community
    :param user: user
    :param instance: community instance
    added/deleted to/from community
    """
    if not user or not user.is_authenticated:
        raise AuthenticationFailed()
    try:
        Team.objects.get(community=instance, user=user)
    except ObjectDoesNotExist as exc:
        raise AuthenticationFailed(f"User {user} is not a member of community {instance}. Error: \"{exc}\"")
    except MultipleObjectsReturned as exc:
        # if somehow there are user duplicates on a community, don't crash
        logger.warning(f"User {user} is in community {instance} multiple times. Error: \"{exc}\"")
