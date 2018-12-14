"""
This module provides Django REST API filters for communities app.
"""

from django_filters import rest_framework as filters
from django_filters import CharFilter

from surf.apps.communities.models import Community


class CommunityFilter(filters.FilterSet):
    """
    Provides filtering functionality for communities requests
    """

    material_id = CharFilter(field_name='collections__materials__external_id')
    is_member = CharFilter(method="filter_is_member")
    is_admin = CharFilter(method="filter_is_admin")

    def filter_is_member(self, qs, name, value):
        return self._filter_by_user_communities(qs, "teams", value)

    def filter_is_admin(self, qs, name, value):
        return self._filter_by_user_communities(qs, "admin_teams", value)

    def _filter_by_user_communities(self, qs, team_attr_name, value):
        """
        Add condition to queryset to filter/exclude of communities
        by user membership
        :param qs: queryset instance
        :param team_attr_name: attribute name of SURF team list
        :param value: if true then filter communities where user is membership,
        if false - exclude these communities
        :return: updated queryset instance
        """

        community_ids = []
        user = _get_and_check_user_from_request(self.request)
        if user:
            user_teams = getattr(user, team_attr_name, [])
            if user_teams:
                community_ids = user_teams.values_list('community__id',
                                                       flat=True)

        value = value in {True, "True", "true", "1"}
        if value:
            # filter user communities
            return qs.filter(id__in=community_ids)
        else:
            # exclude user communities
            return qs.exclude(id__in=community_ids)

    class Meta:
        model = Community
        fields = ('material_id', 'is_member', 'is_admin',)


def _get_and_check_user_from_request(request):
    if request and request.user and request.user.is_authenticated:
        return request.user

    return None
