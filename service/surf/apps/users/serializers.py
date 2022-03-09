"""
This module contains API view serializers for users app.
"""

from rest_framework import serializers

from surf.apps.users.models import User
from surf.apps.communities.models import Community
from surf.apps.materials.models import Collection
from surf.apps.materials.serializers import CollectionSerializer


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User profile instance serializer
    """

    full_name = serializers.CharField(source="email")
    communities = serializers.SerializerMethodField()
    collections = serializers.SerializerMethodField()

    @staticmethod
    def get_communities(obj):
        qs = Community.objects.filter(team__user=obj)
        ids = qs.values_list('id', flat=True)
        return ids

    @staticmethod
    def get_collections(obj):
        qs = Collection.objects.filter(communities__team__user=obj).order_by("title_nl")
        return CollectionSerializer(qs, many=True).data

    class Meta:
        model = User
        fields = ('id', 'full_name', 'is_staff', 'communities', 'collections')
