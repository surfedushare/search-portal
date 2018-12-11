from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator

from surf.apps.materials.models import (
    Collection,
    Material,
    ApplaudMaterial,
    SharedResourceCounter,
    RESOURCE_TYPE_COLLECTION
)


class SharedResourceCounterSerializer(serializers.ModelSerializer):
    sharing_type = serializers.CharField(source="extra")

    class Meta:
        model = SharedResourceCounter
        fields = ('sharing_type', 'counter_value',)


class SearchFilterSerializer(serializers.Serializer):
    external_id = serializers.CharField()

    items = serializers.ListField(
        child=serializers.CharField(allow_null=True, allow_blank=True),
        default=[])


class SearchRequestSerializer(serializers.Serializer):
    search_text = serializers.ListField(child=serializers.CharField())
    page = serializers.IntegerField(required=False, default=1,
                                    validators=[MinValueValidator(1)])

    page_size = serializers.IntegerField(required=False, default=5,
                                         validators=[MinValueValidator(0),
                                                     MaxValueValidator(10)])

    return_records = serializers.BooleanField(required=False, default=True)
    return_filters = serializers.BooleanField(required=False, default=True)

    ordering = serializers.CharField(required=False, allow_blank=True,
                                     allow_null=True)

    author = serializers.CharField(required=False, allow_blank=True,
                                   allow_null=True)

    filters = serializers.ListField(child=SearchFilterSerializer(),
                                    required=False,
                                    allow_null=True)


class SearchRequestShortSerializer(serializers.Serializer):
    search_text = serializers.ListField(child=serializers.CharField())
    page = serializers.IntegerField(required=False, default=1,
                                    validators=[MinValueValidator(1)])

    page_size = serializers.IntegerField(required=False, default=5,
                                         validators=[MinValueValidator(0),
                                                     MaxValueValidator(10)])

    ordering = serializers.CharField(required=False, allow_blank=True,
                                     allow_null=True)


class KeywordsRequestSerializer(serializers.Serializer):
    query = serializers.CharField()


class MaterialRatingSerializer(serializers.Serializer):
    object_id = serializers.CharField()
    rating = serializers.IntegerField(validators=[MinValueValidator(1),
                                                  MaxValueValidator(5)])


class MaterialsRequestSerializer(serializers.Serializer):
    external_id = serializers.CharField(required=False)
    collection_id = serializers.CharField(required=False)
    shared = serializers.CharField(required=False)

    page = serializers.IntegerField(required=False, default=1,
                                    validators=[MinValueValidator(1)])

    page_size = serializers.IntegerField(required=False, default=5,
                                         validators=[MinValueValidator(0),
                                                     MaxValueValidator(10)])


class CollectionMaterialsRequestSerializer(serializers.Serializer):
    page = serializers.IntegerField(required=False, default=1,
                                    validators=[MinValueValidator(1)])

    page_size = serializers.IntegerField(required=False, default=5,
                                         validators=[MinValueValidator(0),
                                                     MaxValueValidator(10)])


class MaterialRatingsRequestSerializer(serializers.Serializer):
    object_id = serializers.CharField(required=False)

    page = serializers.IntegerField(required=False, default=1,
                                    validators=[MinValueValidator(1)])

    page_size = serializers.IntegerField(required=False, default=10,
                                         validators=[MinValueValidator(0),
                                                     MaxValueValidator(10)])


class MaterialRatingResponseSerializer(MaterialRatingSerializer):
    smo_id = serializers.CharField()


class MaterialShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Material
        fields = ('external_id',)


class CollectionShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collection
        fields = ('id',)


class CollectionSerializer(CollectionShortSerializer):
    materials_count = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    communities_count = serializers.SerializerMethodField()
    communities = serializers.SerializerMethodField()
    sharing_counters = serializers.SerializerMethodField()

    owner_name = serializers.CharField(
        source="owner.surfconext_auth.display_name", read_only=True)

    @staticmethod
    def get_sharing_counters(obj):
        counter_key = SharedResourceCounter.create_counter_key(
            RESOURCE_TYPE_COLLECTION,
            str(obj.id))

        qs = SharedResourceCounter.objects.filter(
            counter_key__contains=counter_key)

        return SharedResourceCounterSerializer(many=True).to_representation(
            qs.all())

    @staticmethod
    def get_materials_count(obj):
        return obj.materials.count()

    @staticmethod
    def get_communities_count(obj):
        return getattr(obj, "community_cnt", 0)

    @staticmethod
    def get_communities(obj):
        if obj.communities:
            return [dict(id=c.id, name=c.name) for c in obj.communities.all()]
        else:
            return []

    def get_is_owner(self, obj):
        user = _get_and_check_user_from_context(self.context)
        return bool(user and user.id == obj.owner_id)

    def create(self, validated_data):
        user = _get_and_check_user_from_context(self.context)
        if user:
            validated_data["owner_id"] = user.id

        return super().create(validated_data)

    class Meta:
        model = Collection
        fields = ('id', 'title', 'materials_count', 'communities_count',
                  'is_shared', 'is_owner', 'owner_name', 'communities',
                  'sharing_counters',)


class ApplaudMaterialSerializer(serializers.ModelSerializer):
    material = MaterialShortSerializer()

    def create(self, validated_data):
        external_id = validated_data["material"]["external_id"]
        material, _ = Material.objects.get_or_create(external_id=external_id)
        validated_data["material"] = material

        user = _get_and_check_user_from_context(self.context)
        if user:
            validated_data["user_id"] = user.id

        instance, _ = ApplaudMaterial.objects.get_or_create(**validated_data)

        return instance

    class Meta:
        model = ApplaudMaterial
        fields = ('material',)


def _get_and_check_user_from_context(context):
    request = context.get("request")
    if not request:
        return None

    user = request.user
    if user and user.is_authenticated:
        return user
    else:
        return None
