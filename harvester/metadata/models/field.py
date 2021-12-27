from django.db import models

from metadata.models import MetadataTranslation


class MetadataField(models.Model):

    name = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    translation = models.OneToOneField(MetadataTranslation, on_delete=models.PROTECT, null=False, blank=False)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name
