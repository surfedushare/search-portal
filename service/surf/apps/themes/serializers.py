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

    id = serializers.UUIDField(source="filter_category_item.id")
    description_translations = LocaleHTMLSerializer()
    external_id = serializers.CharField(source="filter_category_item.external_id")

    class Meta:
        model = Theme
        fields = ('id', 'external_id', 'description_translations',)
