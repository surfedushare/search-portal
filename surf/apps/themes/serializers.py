from rest_framework import serializers

from surf.apps.filters.models import FilterCategoryItem


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterCategoryItem
        fields = ('id', 'external_id', 'title',)
