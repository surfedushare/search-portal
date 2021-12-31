from django.db import models
from rest_framework import serializers

from core.utils.elastic import get_es_client
from metadata.models import MetadataTranslation, MetadataTranslationSerializer, MetadataValueSerializer


class MetadataFieldManager(models.Manager):

    def fetch_value_frequencies(self, **kwargs):
        client = get_es_client()
        aggregation_query = {
            field.name: {
                "terms": {
                    "field": field.name,
                    "size": field.size + 500,
                }
            }
            for field in self.annotate(size=models.Count("metadatavalue")).filter(**kwargs).iterator()
        }
        response = client.search(
            index=["latest-nl", "latest-en", "latest-unk"],
            body={"aggs": aggregation_query}
        )
        return {
            field_name: {
                bucket["key"]: bucket["doc_count"]
                for bucket in aggregation["buckets"]
            }
            for field_name, aggregation in response["aggregations"].items()
        }


class MetadataField(models.Model):

    objects = MetadataFieldManager()

    name = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    translation = models.OneToOneField(MetadataTranslation, on_delete=models.PROTECT, null=False, blank=False)
    is_hidden = models.BooleanField(default=False)
    is_manual = models.BooleanField(default=False)
    english_as_dutch = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class MetadataFieldSerializer(serializers.ModelSerializer):

    parent = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    translation = MetadataTranslationSerializer()
    value = serializers.CharField(source="name")
    frequency = serializers.IntegerField(default=0)
    field = serializers.SerializerMethodField()

    max_children = serializers.IntegerField(write_only=True, required=False)

    def get_parent(self, obj):
        return None

    def get_children(self, obj):
        children = obj.metadatavalue_set.select_related("translation").get_cached_trees()
        max_children = self.context["request"].GET.get("max_children", "")
        max_children = int(max_children) if max_children else None
        return MetadataValueSerializer(children, many=True).data[:max_children]

    def get_field(self, obj):
        return None

    class Meta:
        model = MetadataField
        fields = ('id', 'parent', 'is_hidden', 'is_manual', 'children', 'value', 'translation', 'frequency', 'field',
                  'max_children',)
