"""
This module contains API view serializers for filters app.
"""

from rest_framework import serializers

from surf.apps.filters import models
from surf.apps.locale.serializers import LocaleSerializer


class MpttFilterItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    title_translations = LocaleSerializer()
    count = serializers.SerializerMethodField()

    def get_children(self, obj):
        if obj.is_leaf_node():
            return []
        else:
            counts = self.context.get('search_counts', [])
            return MpttFilterItemSerializer(obj.get_children(), many=True, context={'search_counts': counts}).data

    def get_count(self, obj):
        search_counts = self.context.get('search_counts', [])
        if search_counts:
            item = search_counts.get(obj.external_id, None)
            if item:
                return item.get('count', 0)
        return 0

    class Meta:
        model = models.MpttFilterItem
        fields = ('name', 'parent', 'title_translations', 'external_id', 'is_hidden', 'children', 'count',)
