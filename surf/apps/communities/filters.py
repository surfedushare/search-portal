from django_filters import rest_framework as filters
from django_filters import CharFilter

from surf.apps.communities.models import Community


class CommunityFilter(filters.FilterSet):
    material_id = CharFilter(field_name='collections__materials__external_id')
    is_member = CharFilter(method="filter_is_member")
    is_admin = CharFilter(method="filter_is_admin")

    def filter_is_member(self, qs, name, value):
        return self._filter_by_user_communities(qs, "communities", value)

    def filter_is_admin(self, qs, name, value):
        return self._filter_by_user_communities(qs, "admin_communities", value)

    def _filter_by_user_communities(self, qs, community_attr_name, value):
        community_ids = []
        user = _get_and_check_user_from_request(self.request)
        if user:
            user_communities = getattr(user, community_attr_name, [])
            if user_communities:
                community_ids = user_communities.values_list('id', flat=True)

        value = value in {True, "True", "true", "1"}
        if value:
            return qs.filter(id__in=community_ids)
        else:
            return qs.exclude(id__in=community_ids)

    class Meta:
        model = Community
        fields = ('material_id', 'is_member', 'is_admin',)


def _get_and_check_user_from_request(request):
    if not request:
        return None

    if request.user and request.user.is_authenticated:
        return request.user

    return None
