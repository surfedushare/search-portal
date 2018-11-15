from django_filters import rest_framework as filters
from django_filters import CharFilter

from surf.apps.communities.models import Community


class CommunityFilter(filters.FilterSet):
    material_id = CharFilter(field_name='collections__materials__external_id')

    class Meta:
        model = Community
        fields = ('material_id',)
