"""
This module contains API view serializers for users app.
"""

from rest_framework import serializers

from surf.apps.users.models import User
from surf.apps.communities.models import Community


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User profile instance serializer
    """

    full_name = serializers.CharField(source="surfconext_auth.display_name")
    is_admin = serializers.SerializerMethodField()
    communities = serializers.SerializerMethodField()
    collections = serializers.SerializerMethodField()

    @staticmethod
    def get_communities(obj):
        qs = Community.objects.filter(team__user=obj)
        ids = qs.values_list('id', flat=True)
        return ids

    @staticmethod
    def get_collections(obj):
        qs = Community.objects.filter(team__user=obj)
        ids = qs.values_list('collections__id', flat=True)
        return list(set(ids))

    @staticmethod
    def get_is_admin(obj):
        return Community.objects.filter(team__user=obj).exists()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'is_admin', 'communities', 'collections')
