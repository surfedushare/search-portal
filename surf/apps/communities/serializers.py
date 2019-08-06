"""
This module contains API view serializers for communities app.
"""

from rest_framework import serializers

from surf.apps.communities.models import Community
from surf.apps.filters.models import FilterCategoryItem
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

    external_id = serializers.CharField(source="surf_team.external_id")
    members_count = serializers.SerializerMethodField()
    collections_count = serializers.SerializerMethodField()
    materials_count = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    title_translations = LocaleSerializer()
    description_translations = LocaleHTMLSerializer()

    @staticmethod
    def get_name(obj):
        if obj.name:
            return obj.name
        else:
            return obj.surf_team.name

    @staticmethod
    def get_description(obj):
        if obj.description:
            return obj.description
        else:
            return obj.surf_team.description

    @staticmethod
    def get_members_count(obj):
        try:
            return obj.surf_team.members.count()
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

    def get_is_admin(self, obj):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            return obj.surf_team.admins.filter(id=request.user.id).exists()
        return False

    def get_is_member(self, obj):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            return obj.surf_team.members.filter(id=request.user.id).exists()
        return False

    class Meta:
        model = Community
        fields = ('id', 'external_id', 'name', 'description', 'website_url',
                  'logo', 'featured_image', 'members_count',
                  'collections_count', 'materials_count',
                  'is_admin', 'is_member', 'title_translations', 'description_translations',)


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
        model = FilterCategoryItem
        fields = ('id', 'external_id', 'title', 'materials_count',)
