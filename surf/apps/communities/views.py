from django.db.models import Q, Count

from rest_framework.viewsets import GenericViewSet

from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin
)

from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import action
from rest_framework.response import Response

from surf.apps.communities.models import Community
from surf.apps.materials.models import Collection

from surf.apps.communities.serializers import (
    CommunitySerializer,
    CommunityUpdateSerializer
)

from surf.apps.materials.serializers import (
    CollectionSerializer,
    CollectionShortSerializer
)

from surf.apps.communities.filters import CommunityFilter


class CommunityViewSet(ListModelMixin,
                       RetrieveModelMixin,
                       UpdateModelMixin,
                       GenericViewSet):
    """
    View class that provides `GET` and `UPDATE` methods for Community.
    """

    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    filter_class = CommunityFilter
    permission_classes = []

    def get_serializer_class(self):
        if self.action == 'update':
            return CommunityUpdateSerializer

        return CommunitySerializer

    def update(self, request, *args, **kwargs):
        # only active admins can update community
        self._check_access(request.user, instance=self.get_object())
        return super().update(request, *args, **kwargs)

    @action(methods=['get', 'post', 'delete'], detail=True)
    def collections(self, request, pk=None, **kwargs):
        instance = self.get_object()

        if request.method in {"POST", "DELETE"}:
            # validate request parameters
            serializer = CollectionShortSerializer(many=True,
                                                   data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.initial_data

            self._check_access(request.user,
                               instance=instance,
                               collection_ids=[d["id"] for d in data])

            if request.method == "POST":
                self._add_collections(instance, data)
            elif request.method == "DELETE":
                self._delete_collections(instance, data)

        res = []
        if instance.collections.exists():
            qs = instance.collections.annotate(
                community_cnt=Count('communities'))

            res = CollectionSerializer(many=True).to_representation(qs.all())

        return Response(res)

    @staticmethod
    def _add_collections(instance, collections):
        """
        Add collections to community
        :param instance: community instance
        :param collections: added collections
        :return:
        """
        for c in collections:
            try:
                c = Collection.objects.get(id=c["id"])
                instance.collections.add(c)
            except Collection.DoesNotExist:
                pass

    @staticmethod
    def _delete_collections(instance, collections):
        """
        Delete collections from community
        :param instance: community instance
        :param collections: deleted collections
        :return:
        """
        for c in collections:
            try:
                c = Collection.objects.get(id=c["id"])
                instance.collections.remove(c)
            except Collection.DoesNotExist:
                pass

    @staticmethod
    def _check_access(user, instance=None, collection_ids=None):
        """
        Check if user is active and admin of community
        :param user: user
        :param instance: community instance
        :param collection_ids: list of identifiers of collections
        added/deleted to/from community
        """
        if not user or not user.is_active:
            raise AuthenticationFailed()

        if instance and (not instance.admins.filter(id=user.id).exists()):
            raise AuthenticationFailed()

        if collection_ids:
            qs = Collection.objects.filter(Q(id__in=collection_ids),
                                           ~Q(owner_id=user.id))
            if qs.exists():
                raise AuthenticationFailed()
