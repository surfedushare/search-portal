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


class CommunityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityDetail
        exclude = ('id', 'community',)


class CommunitySerializer(serializers.ModelSerializer):
    """
    Community instance serializer for get methods
    """

    external_id = serializers.CharField()
    members_count = serializers.SerializerMethodField()
    collections_count = serializers.SerializerMethodField()
    materials_count = serializers.SerializerMethodField()
    publish_status = serializers.SerializerMethodField()
    community_details = CommunityDetailSerializer(many=True)

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

    def create(self, validated_data):
        details_data = validated_data.pop('community_details')
        community = Community.objects.create(**validated_data)
        for detail_data in details_data:
            CommunityDetail.objects.create(community=community, **detail_data)
        return community

    def update(self, instance, validated_data):
        # we could update the community instance itself, however the only value that can be updated
        # is the name which is only used internally so it's not required through the API
        details_data = validated_data.pop('community_details')

        community_details = instance.community_details.all()

        new = {data['language_code'].upper() for data in details_data}
        existing = {detail.language_code for detail in community_details}
        languages_to_update = new.intersection(existing)
        languages_to_create = new.difference(existing)

        languages_to_update = [details for details in details_data if details['language_code'] in languages_to_update]
        languages_to_create = [details for details in details_data if details['language_code'] in languages_to_create]

        for language in languages_to_create:
            detail_object = CommunityDetail.objects.create(community=instance, **language)
            detail_object.clean()
            detail_object.save()

        for language in languages_to_update:
            detail_object = instance.community_details.get(language_code=language['language_code'].upper())
            for attr, value in language.items():
                if value is not None:
                    setattr(detail_object, attr, value)
            detail_object.clean()
            detail_object.save()
        return instance

    class Meta:
        model = Community
        fields = ('id', 'external_id', 'name', 'members_count',
                  'collections_count', 'materials_count', 'publish_status',
                  'community_details',)


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
