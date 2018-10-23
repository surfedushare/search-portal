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
