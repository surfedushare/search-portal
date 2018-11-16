from rest_framework import serializers

from surf.apps.materials.models import (
    Collection,
    Material,
    ApplaudMaterial
)


class SearchFilterSerializer(serializers.Serializer):
    external_id = serializers.CharField()
    items = serializers.ListField(child=serializers.CharField())


class SearchRequestSerializer(serializers.Serializer):
    search_text = serializers.ListField(child=serializers.CharField())
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=5)
    return_records = serializers.BooleanField(required=False, default=True)
    return_filters = serializers.BooleanField(required=False, default=True)

    ordering = serializers.CharField(required=False, allow_blank=True,
                                     allow_null=True)

    author = serializers.CharField(required=False, allow_blank=True,
                                   allow_null=True)

    filters = serializers.ListField(child=SearchFilterSerializer(),
                                    required=False,
                                    allow_null=True)


class KeywordsRequestSerializer(serializers.Serializer):
    query = serializers.CharField()


class MaterialsRequestSerializer(serializers.Serializer):
    external_id = serializers.CharField(required=False)
    collection_id = serializers.CharField(required=False)
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=5)


class CollectionMaterialsRequestSerializer(serializers.Serializer):
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=5)


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

    @staticmethod
    def get_materials_count(obj):
        return obj.materials.count()

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
        fields = ('id', 'title', 'materials_count',
                  'is_shared', 'is_owner',)


class ApplaudMaterialSerializer(serializers.ModelSerializer):
    material = MaterialShortSerializer()

    def create(self, validated_data):
        material_external_id = validated_data["material"]["external_id"]
        material, _ = Material.objects.get_or_create(
            external_id=material_external_id,
            defaults=dict(external_id=material_external_id))
        validated_data["material"] = material

        user = _get_and_check_user_from_context(self.context)
        if user:
            validated_data["user_id"] = user.id

        instance, _ = ApplaudMaterial.objects.get_or_create(
            **validated_data,
            defaults=validated_data)

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
