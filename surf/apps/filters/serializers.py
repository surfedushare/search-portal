from rest_framework import serializers

from surf.apps.filters import models


class FilterCategoryItemSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="external_id")

    class Meta:
        model = models.FilterCategoryItem
        fields = ('id', 'title',)


class FilterCategorySerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="edurep_field_id")
    items = FilterCategoryItemSerializer(many=True)

    class Meta:
        model = models.FilterCategory
        fields = ('id', 'title', 'items',)
