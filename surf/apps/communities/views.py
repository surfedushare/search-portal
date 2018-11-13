from rest_framework.viewsets import GenericViewSet

from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin
)

from rest_framework.exceptions import AuthenticationFailed

from surf.apps.communities.models import Community

from surf.apps.communities.serializers import (
    CommunitySerializer,
    CommunityUpdateSerializer
)


class CommunityViewSet(ListModelMixin,
                       RetrieveModelMixin,
                       UpdateModelMixin,
                       GenericViewSet):
    """
    View class that provides `GET` and `UPDATE` methods for Community.
    """

    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = []

    def get_serializer_class(self):
        if self.action == 'update':
            return CommunityUpdateSerializer

        return CommunitySerializer

    def update(self, request, *args, **kwargs):
        # only active admins can update community
        self._check_access(request.user, instance=self.get_object())
        return super().update(request, *args, **kwargs)

    @staticmethod
    def _check_access(user, instance=None):
        """
        Check if user is active and admin of community
        :param user: user
        :param instance: community instance
        """
        if not user or not user.is_active:
            raise AuthenticationFailed()

        if instance and (not instance.admins.filter(id=user.id).exists()):
            raise AuthenticationFailed()
