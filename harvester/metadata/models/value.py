from django.db import models
from mptt.models import MPTTModel

from metadata.models import MetadataTranslation, MetadataField


class MetadataValue(MPTTModel):

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    field = models.ForeignKey(MetadataField, on_delete=models.CASCADE, null=False, blank=False)
    value = models.CharField(max_length=255, blank=False, null=False)
    translation = models.OneToOneField(MetadataTranslation, on_delete=models.PROTECT, null=False, blank=False)
    frequency = models.PositiveIntegerField()
    is_manual = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        unique_together = ("field", "value",)
