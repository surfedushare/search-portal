"""
This module contains API view serializers for filters app.
"""

from rest_framework import serializers

from surf.apps.filters import models
from surf.apps.locale.serializers import LocaleSerializer


class FilterShortSerializer(serializers.ModelSerializer):
    """
    Filter instance serializer with a few fields
    """

    class Meta:
        model = models.Filter
        fields = ('id', 'title', 'start_date', 'end_date', 'materials_count',)


class MpttFilterItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    title_translations = LocaleSerializer()
    count = serializers.SerializerMethodField()

    def get_children(self, obj):
        if obj.is_leaf_node():
            return []
        else:
            counts = self.context.get('search_counts', [])
            if counts:
                return MpttFilterItemSerializer(obj.get_children(), many=True, context={'search_counts': counts}).data
            else:
                return MpttFilterItemSerializer(obj.get_children(), many=True).data

    def get_count(self, obj):
        search_counts = self.context.get('search_counts', [])
        if search_counts:
            item = search_counts.get(obj.external_id, None)
            if item:
                return item.get('count', 0)
        return

    class Meta:
        model = models.MpttFilterItem
        fields = ('id', 'name', 'parent', 'title_translations', 'external_id', 'enabled_by_default', 'is_hidden',
                  'item_count', 'children', 'count')


class FilterSerializer(FilterShortSerializer):
    """
    Filter instance serializer with filter items
    """

    items = MpttFilterItemSerializer(many=True, required=False)

    def create(self, validated_data):
        # raise error in user is not set or does not authenticated
        request = self.context.get("request")
        if not request:
            raise TypeError("Invalid user")

        user = request.user
        if not user or not user.is_authenticated:
            raise TypeError("Invalid user")

        validated_data["owner_id"] = user.id
        validated_data.pop("items", None)

        rv = super().create(validated_data)

        # create filter items
        for it in self.initial_data.get("items", []):
            rv.items.create(category_item_id=it["category_item_id"])

        return rv

    def update(self, instance, validated_data):
        validated_data.pop("items", None)

        instance = super().update(instance, validated_data)

        if "items" in self.initial_data:
            # update filter items
            instance.items.all().delete()
            for it in self.initial_data.get("items", []):
                instance.items.create(category_item_id=it["category_item_id"])

        return instance

    class Meta:
        model = models.Filter
        fields = ('id', 'title', 'items', 'start_date', 'end_date',
                  'materials_count',)
