"""
This module contains API view serializers for themes app.
"""

from rest_framework import serializers

from surf.apps.themes.models import Theme
from surf.apps.filters.models import MpttFilterItem
from surf.apps.locale.serializers import LocaleSerializer, LocaleHTMLSerializer
from surf.apps.filters.serializers import MpttFilterItemSerializer


class ThemeSerializer(serializers.ModelSerializer):
    """
    Theme instance serializer
    """

    id = serializers.UUIDField(source="mptt_filter_category_item.id")
    title = serializers.CharField(source="mptt_filter_category_item.name")
    title_translations = LocaleSerializer()
    description_translations = LocaleHTMLSerializer()

    class Meta:
        model = Theme
        fields = ('id', 'external_id', 'title', 'description', 'title_translations', 'description_translations',)


class ThemeDisciplineSerializer(MpttFilterItemSerializer):
    """
    Theme discipline instance serializer
    """

    materials_count = serializers.SerializerMethodField()

    def get_materials_count(self, obj):
        try:
            if self.context:
                drilldowns = self.context["extra"]["drilldowns"]
                return drilldowns.get(obj.external_id, 0)
        except KeyError:
            pass

        return 0

    class Meta:
        model = MpttFilterItem
        fields = '__all__'
