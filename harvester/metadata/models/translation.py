from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class MetadataTranslation(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    nl = models.CharField(_("Dutch"), max_length=255, null=False, blank=False)
    en = models.CharField(_("English"), max_length=255, null=False, blank=True)
    is_fuzzy = models.BooleanField(default=False)

    def clean(self):
        if not self.en and self.nl:
            self.en = self.nl

    def __str__(self):
        return f"{self.nl} // {self.en}"


class MetadataTranslationSerializer(serializers.ModelSerializer):

    class Meta:
        model = MetadataTranslation
        fields = ('en', 'nl',)
