from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet
)

from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated

from surf.apps.filters.models import (
    FilterCategory,
    Filter
)

from surf.apps.filters.serializers import (
    FilterCategorySerializer,
    FilterSerializer
)


class FilterCategoryViewSet(ListModelMixin,
                            GenericViewSet):

    queryset = FilterCategory.objects.all()
    serializer_class = FilterCategorySerializer
    permission_classes = []


class FilterViewSet(ModelViewSet):
    queryset = Filter.objects.none()
    serializer_class = FilterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if not user or not user.is_active:
            return Filter.objects.none()

        return Filter.objects.filter(owner_id=user.id).all()
