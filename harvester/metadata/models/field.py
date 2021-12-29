from django.db import models

from core.utils.elastic import get_es_client
from metadata.models import MetadataTranslation


class MetadataFieldManager(models.Manager):

    def fetch_value_frequencies(self, filters=None):
        filters = filters or {}
        client = get_es_client()
        aggregation_query = {
            field.name: {
                "terms": {
                    "field": field.name,
                    "size": field.size + 500,
                }
            }
            for field in self.annotate(size=models.Count("metadatavalue")).filter(**filters).iterator()
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
    english_as_dutch = models.BooleanField(default=False)

    def __str__(self):
        return self.name
