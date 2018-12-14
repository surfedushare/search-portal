"""
This module contains API view serializers for filters app.
"""

from rest_framework import serializers

from surf.apps.filters import models


class FilterCategoryItemSerializer(serializers.ModelSerializer):
    """
    Filter category item instance serializer
    """

    class Meta:
        model = models.FilterCategoryItem
        fields = ('id', 'external_id', 'title',)


class FilterCategorySerializer(serializers.ModelSerializer):
    """
    Filter category instance serializer
    """

    external_id = serializers.CharField(source="edurep_field_id")
    items = FilterCategoryItemSerializer(many=True)

    class Meta:
        model = models.FilterCategory
        fields = ('id', 'external_id', 'title', 'items',)


class FilterItemSerializer(serializers.ModelSerializer):
    """
    Filter item instance serializer
    """

    category_item_id = serializers.CharField(source="category_item.id")

    category_id = serializers.CharField(source="category_item.category.id",
                                        read_only=True)

    class Meta:
        model = models.FilterCategoryItem
        fields = ('id', 'category_item_id', 'category_id',)


class FilterShortSerializer(serializers.ModelSerializer):
    """
    Filter instance serializer with a few fields
    """

    class Meta:
        model = models.Filter
        fields = ('id', 'title', 'start_date', 'end_date', 'materials_count',)


class FilterSerializer(FilterShortSerializer):
    """
    Filter instance serializer with filter items
    """

    items = FilterItemSerializer(many=True, required=False)

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
