from rest_framework import serializers

from surf.apps.themes.models import Theme


class ThemeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="filter_category_item.id")
    title = serializers.CharField(source="filter_category_item.title")

    class Meta:
        model = Theme
        fields = ('id', 'external_id', 'title', 'description',)
