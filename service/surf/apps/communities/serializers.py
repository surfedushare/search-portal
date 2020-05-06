"""
This module contains API view serializers for communities app.
"""
from collections import OrderedDict

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from surf.apps.communities.models import Community, CommunityDetail
from surf.apps.communities.models import PublishStatus
from surf.apps.filters.models import MpttFilterItem
from surf.apps.filters.serializers import MpttFilterItemSerializer
from surf.apps.filters.utils import add_default_material_filters
from surf.vendor.search.searchselector import get_search_client
from django.core.exceptions import ValidationError
from rest_framework.exceptions import APIException


class CommunityDetailValidationError(APIException):
    status_code = 400


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
        try:
            detail_object.clean_fields()
            detail_object.clean()
            # We check description separately, because it shouldn't be required in the admin
            if not detail_object.description.strip():
                raise ValidationError({"description": _("This field cannot be blank.")})
            detail_object.save()
        except ValidationError as exc:
            return exc

    def update(self, instance, validated_data):
        # TODO: can we refactor this to use DRF serializer validation instead of
        # attr getters and setters with freaky exception returning?

        # First we update everything on the community itself
        publish_status = validated_data.get("publish_status", None)
        if publish_status is not None:
            instance.publish_status = publish_status
            instance.save()

        # Then we update the language specific data
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
        # Prepare prefill website urls
        website_urls = {
            community_detail['language_code']: community_detail.get('website_url', None)
            for community_detail in details_data
        }
        for language, website_url in website_urls.items():
            if website_url and not website_url.startswith("http"):
                website_urls[language] = "https://" + website_url
            elif not website_url and language == "NL" and website_urls["EN"]:
                website_urls[language] = website_urls["EN"]
            elif not website_url and language == "EN" and website_urls["NL"]:
                website_urls[language] = website_urls["NL"]
        # Actual update of community details
        result_nl = result_en = None
        for community_detail in details_data:
            community_detail["website_url"] = website_urls[community_detail["language_code"]]
            if community_detail['language_code'] == 'NL':
                result_nl = self.update_community_details(community_instance=instance,
                                                          community_details=community_detail,
                                                          logo=logo_nl, featured_image=featured_image_nl)
            if community_detail['language_code'] == 'EN':
                result_en = self.update_community_details(community_instance=instance,
                                                          community_details=community_detail,
                                                          logo=logo_en, featured_image=featured_image_en)

        if not result_nl and not result_en:
            return instance
        feedback = {}
        if result_nl:
            feedback['NL'] = result_nl
        if result_en:
            feedback['EN'] = result_en
        raise CommunityDetailValidationError(detail=feedback)

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
