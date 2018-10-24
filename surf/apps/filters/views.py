from rest_framework import (
    viewsets,
    mixins
)

from surf.apps.filters import models, serializers


class FilterCategoryViewSet(mixins.ListModelMixin,
                            viewsets.GenericViewSet):

    queryset = models.FilterCategory.objects.all()
    serializer_class = serializers.FilterCategorySerializer
    permission_classes = []


class FilterViewSet(viewsets.ModelViewSet):
    queryset = models.Filter.objects.none()
    serializer_class = serializers.FilterSerializer
    permission_classes = []

    def get_queryset(self):
        user = self.request.user

        if not user or not user.is_active:
            return models.Filter.objects.none()

        return models.Filter.objects.filter(owner_id=user.id).all()
