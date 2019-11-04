"""
This module contains API view serializers for communities app.
"""

from rest_framework import serializers

from surf.apps.communities.models import Community
from surf.apps.filters.models import MpttFilterItem
from surf.apps.filters.serializers import FilterCategoryItemSerializer
from surf.apps.locale.serializers import LocaleSerializer, LocaleHTMLSerializer


class CommunityUpdateSerializer(serializers.ModelSerializer):
    """
    Community instance serializer for update methods
    """

    class Meta:
        model = Community
        fields = ('name', 'description', 'website_url',
                  'logo', 'featured_image',)


class CommunitySerializer(CommunityUpdateSerializer):
    """
    Community instance serializer for get methods
    """

    external_id = serializers.CharField()
    members_count = serializers.SerializerMethodField()
    collections_count = serializers.SerializerMethodField()
    materials_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    title_translations = LocaleSerializer()
    description_translations = LocaleHTMLSerializer()

    @staticmethod
    def get_members_count(obj):
        try:
            return obj.new_members.count()
        except Exception as exc:
            print(exc)
            return 0

    @staticmethod
    def get_collections_count(obj):
        return obj.collections.count()

    @staticmethod
    def get_materials_count(obj):
        ids = obj.collections.values_list("materials__id", flat=True)
        ids = [i for i in ids if i]
        return len(set(ids))

    def get_is_member(self, obj):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            return obj.new_members.filter(id=request.user.id).exists()
        return False

    class Meta:
        model = Community
        fields = ('id', 'external_id', 'name', 'description', 'website_url',
                  'logo', 'featured_image', 'members_count',
                  'collections_count', 'materials_count',
                  'is_member', 'title_translations', 'description_translations',)


class CommunityDisciplineSerializer(FilterCategoryItemSerializer):
    """
    Community discipline instance serializer
    """

    materials_count = serializers.SerializerMethodField()

    def get_materials_count(self, obj):
        try:
            if self.context:
                drilldowns = self.context["extra"]["drilldowns"]
                return drilldowns.get(obj.external_id, 0)
        except KeyError:
            pass

        return 0

    class Meta:
        model = MpttFilterItem
        fields = ('id', 'external_id', 'name', 'materials_count',)
