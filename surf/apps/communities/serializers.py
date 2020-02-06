"""
This module contains API view serializers for communities app.
"""

from collections import OrderedDict

from rest_framework import serializers

from surf.apps.communities.models import Community, CommunityDetail
from surf.apps.communities.models import PublishStatus
from surf.apps.filters.models import MpttFilterItem
from surf.apps.filters.serializers import MpttFilterItemSerializer
from surf.apps.filters.utils import add_default_material_filters
from surf.vendor.search.searchselector import get_search_client


class CommunityUpdateSerializer(serializers.ModelSerializer):
    """
    Community instance serializer for update methods
    """

    class Meta:
        model = Community
        fields = ('name',)


class CommunityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityDetail
        exclude = ('id', 'community',)


class CommunitySerializer(CommunityUpdateSerializer):
    """
    Community instance serializer for get methods
    """

    external_id = serializers.CharField()
    members_count = serializers.SerializerMethodField()
    collections_count = serializers.SerializerMethodField()
    materials_count = serializers.SerializerMethodField()
    language_details = serializers.SerializerMethodField()
    publish_status = serializers.SerializerMethodField()

    @staticmethod
    def get_members_count(obj):
        try:
            return obj.members.count()
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

    @staticmethod
    def get_publish_status(obj):
        return str(PublishStatus.get(obj.publish_status))

    @staticmethod
    def get_language_details(obj):
        details = CommunityDetail.objects.filter(community=obj).all()
        return [CommunityDetailSerializer(detail).data for detail in details]

    class Meta:
        model = Community
        fields = ('id', 'external_id', 'name', 'members_count',
                  'collections_count', 'materials_count', 'publish_status',
                  'language_details',)


class CommunityDisciplineSerializer(MpttFilterItemSerializer):
    """
    Community discipline instance serializer
    """

    materials_count = serializers.SerializerMethodField()

    def get_materials_count(self, obj):
        if obj.external_id:
            ac = get_search_client()
            filters = [OrderedDict(external_id=obj.parent.external_id, items=[obj.external_id])]
            tree = self.context["mptt_tree"]
            filters = add_default_material_filters(filters, tree)
            res = ac.search([], filters=filters, page_size=0)
            return res['recordcount']

        return 0

    class Meta:
        model = MpttFilterItem
        fields = ('id', 'external_id', 'name', 'materials_count',)
