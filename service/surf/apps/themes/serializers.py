"""
This module contains API view serializers for themes app.
"""
from rest_framework import serializers

from surf.apps.themes.models import Theme
from surf.apps.locale.serializers import LocaleHTMLSerializer


class ThemeSerializer(serializers.ModelSerializer):
    """
    Theme instance serializer
    """

    id = serializers.UUIDField()
    description_translations = LocaleHTMLSerializer()
    external_id = serializers.CharField()

    class Meta:
        model = Theme
        fields = ('id', 'nl_slug', 'en_slug', 'external_id', 'description_translations',)
