from django_filters import rest_framework as filters

from surf.apps.materials.models import ApplaudMaterial


class ApplaudMaterialFilter(filters.FilterSet):

    class Meta:
        model = ApplaudMaterial
        fields = ('material__external_id',)
