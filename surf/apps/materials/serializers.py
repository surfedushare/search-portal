from rest_framework import serializers

from surf.apps.materials.models import (
    Collection,
    Material
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


class CollectionSerializer(serializers.ModelSerializer):
    materials_count = serializers.SerializerMethodField()

    def get_materials_count(self, obj):
        return obj.materials.count()

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        validated_data["owner_id"] = user.id
        return super().create(validated_data)

    class Meta:
        model = Collection
        fields = ('id', 'title', 'materials_count',)
