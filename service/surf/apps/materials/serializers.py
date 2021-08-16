"""
This module contains API view serializers for materials app.
"""

from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from surf.vendor.elasticsearch.serializers import SearchResultSerializer
from surf.apps.communities.serializers import CommunitySerializer
from surf.apps.materials.models import (
    Collection,
    Material,
    SharedResourceCounter,
    RESOURCE_TYPE_COLLECTION,
    PublishStatus,
)
from surf.apps.filters.serializers import MpttFilterItemSerializer


class SharedResourceCounterSerializer(serializers.ModelSerializer):
    """
    Shared resource counter instance serializer
    """

    sharing_type = serializers.CharField(source="extra")

    class Meta:
        model = SharedResourceCounter
        fields = ('sharing_type', 'counter_value',)


class SearchFilterCategorySerializer(serializers.Serializer):
    """
    Serializer for filters in material search request
    """

    external_id = serializers.CharField()
    items = serializers.ListField(child=serializers.CharField())


class SearchSerializer(serializers.Serializer):
    """
    Serializer for material search request
    """

    search_text = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
    page = serializers.IntegerField(required=False, default=1, validators=[MinValueValidator(1)])
    page_size = serializers.IntegerField(required=False, default=5,
                                         validators=[MinValueValidator(0), MaxValueValidator(10)])
    ordering = serializers.CharField(required=False, allow_blank=True, default=None, allow_null=True, write_only=True)
    filters = SearchFilterCategorySerializer(many=True, write_only=True, default=[])

    results = SearchResultSerializer(many=True, read_only=True)
    records_total = serializers.IntegerField(read_only=True)
    filter_categories = MpttFilterItemSerializer(many=True, read_only=True)


class KeywordsRequestSerializer(serializers.Serializer):
    """
    Serializer for keywords request
    """

    query = serializers.CharField(write_only=True)


class SimilaritySerializer(serializers.Serializer):
    """
    Serializer for similarity request
    """

    external_id = serializers.CharField(write_only=True, required=True)
    language = serializers.CharField(write_only=True, required=True)

    results = SearchResultSerializer(many=True, read_only=True)
    records_total = serializers.IntegerField(read_only=True)


class MaterialsRequestSerializer(serializers.Serializer):
    """
    Serializer for materials request
    """

    external_id = serializers.CharField(required=False)
    collection_id = serializers.CharField(required=False)
    shared = serializers.CharField(required=False)

    page = serializers.IntegerField(required=False, default=1,
                                    validators=[MinValueValidator(1)])

    page_size = serializers.IntegerField(required=False, default=1,
                                         validators=[MinValueValidator(0),
                                                     MaxValueValidator(10)])
    count_view = serializers.BooleanField(required=False, default=False)


class CollectionMaterialsRequestSerializer(serializers.Serializer):
    """
    Serializer for collection materials request
    """

    page = serializers.IntegerField(required=False, default=1,
                                    validators=[MinValueValidator(1)])

    page_size = serializers.IntegerField(required=False, default=5,
                                         validators=[MinValueValidator(0),
                                                     MaxValueValidator(10)])


class MaterialRatingsRequestSerializer(serializers.Serializer):
    """
    Serializer for materials ratings request
    """

    object_id = serializers.CharField(required=False)

    page = serializers.IntegerField(required=False, default=1,
                                    validators=[MinValueValidator(1)])

    page_size = serializers.IntegerField(required=False, default=10,
                                         validators=[MinValueValidator(0),
                                                     MaxValueValidator(10)])


class MaterialShortSerializer(serializers.ModelSerializer):
    """
    Material instance serializer with external id only
    """

    class Meta:
        model = Material
        fields = ('external_id',)


class CollectionMaterialPositionSerializer(serializers.Serializer):
    """
    Collection Material instance serializer with external_id and position
    """

    external_id = serializers.CharField(required=False)

    position = serializers.IntegerField(required=False)


class CollectionShortSerializer(serializers.ModelSerializer):
    """
    Minimal collection instance serializer
    """

    class Meta:
        model = Collection
        fields = ('id', 'title_nl', 'title_en', 'position')


class CollectionSerializer(CollectionShortSerializer):
    """
    Collection instance serializer
    """

    title_nl = serializers.CharField()
    title_en = serializers.CharField()
    materials_count = serializers.SerializerMethodField()
    communities_count = serializers.SerializerMethodField()
    communities = CommunitySerializer(many=True, read_only=True)
    sharing_counters = serializers.SerializerMethodField()
    position = serializers.IntegerField(required=False)

    @staticmethod
    def get_sharing_counters(obj):
        counter_key = SharedResourceCounter.create_counter_key(
            RESOURCE_TYPE_COLLECTION,
            str(obj.id))

        qs = SharedResourceCounter.objects.filter(
            counter_key__contains=counter_key)

        return SharedResourceCounterSerializer(many=True).to_representation(
            qs.all())

    def validate(self, attrs):
        if not self.get_materials_count(self.instance) and attrs.get("publish_status", None) == PublishStatus.PUBLISHED:
            raise ValidationError("Can't publish a collection if it doesn't have materials")
        return attrs

    @staticmethod
    def get_materials_count(obj):
        if not obj:
            return 0
        return obj.materials.filter(deleted_at=None).count()

    @staticmethod
    def get_communities_count(obj):
        return getattr(obj, "community_cnt", 0)

    class Meta:
        model = Collection
        fields = ('id', 'title_nl', 'title_en', 'materials_count', 'communities_count',
                  'communities', 'sharing_counters', 'publish_status', 'position')


def _get_and_check_user_from_context(context):
    request = context.get("request")
    if not request:
        return None

    user = request.user
    if user and user.is_authenticated:
        return user
    else:
        return None
