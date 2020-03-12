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
    community_details = CommunityDetailSerializer(many=True, required=False)
    community_details_update = serializers.JSONField(write_only=True)
    logo_nl = serializers.ImageField(write_only=True, allow_null=True, required=False)
    logo_en = serializers.ImageField(write_only=True, allow_null=True, required=False)
    featured_image_nl = serializers.ImageField(write_only=True, allow_null=True, required=False)
    featured_image_en = serializers.ImageField(write_only=True, allow_null=True, required=False)
    deleted_logos = serializers.JSONField(write_only=True, required=False)

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
        community.clean()
        community.save()
        for detail_data in details_data:
            detail_object = CommunityDetail.objects.create(community=community, **detail_data)
            detail_object.clean()
            detail_object.save()
        return community

    def update_community_details(self, community_instance, community_details, logo, featured_image):
        language_code = community_details['language_code'].upper()
        detail_object = community_instance.community_details.get(language_code=language_code)
        for attr, value in community_details.items():
            if value is not None:
                setattr(detail_object, attr, value)

        if logo is not None:
            setattr(detail_object, 'logo', logo)
        if featured_image is not None:
            setattr(detail_object, 'featured_image', featured_image)
        detail_object.clean()
        detail_object.save()

    def update(self, instance, validated_data):
        # we could update the community instance itself, however the only value that can be updated
        # is the name which is only used internally so it's not required through the API
        details_data = validated_data.pop('community_details_update')
        logo_nl = None
        if 'logo_nl' in validated_data.keys():
            logo_nl = validated_data.pop('logo_nl')
        logo_en = None
        if 'logo_en' in validated_data.keys():
            logo_en = validated_data.pop('logo_en')
        featured_image_nl = None
        if 'featured_image_nl' in validated_data.keys():
            featured_image_nl = validated_data.pop('featured_image_nl')
        featured_image_en = None
        if 'featured_image_en' in validated_data.keys():
            featured_image_en = validated_data.pop('featured_image_en')
        if 'deleted_logos' in validated_data.keys():
            keys = validated_data.pop('deleted_logos')
            for key in keys:
                if key == 'logo_nl':
                    logo_nl = ''
                if key == 'logo_en':
                    logo_en = ''
                if key == 'featured_image_nl':
                    featured_image_nl = ''
                if key == 'featured_image_en':
                    featured_image_en = ''
        for community_detail in details_data:
            if community_detail['language_code'] == 'NL':
                self.update_community_details(community_instance=instance, community_details=community_detail,
                                              logo=logo_nl, featured_image=featured_image_nl)
            if community_detail['language_code'] == 'EN':
                self.update_community_details(community_instance=instance, community_details=community_detail,
                                              logo=logo_en, featured_image=featured_image_en)
        return instance

    class Meta:
        model = Community
        fields = ('id', 'external_id', 'members_count',
                  'collections_count', 'materials_count', 'publish_status',
                  'community_details', 'community_details_update',
                  'logo_nl', 'logo_en', 'featured_image_nl', 'featured_image_en', 'deleted_logos')


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
