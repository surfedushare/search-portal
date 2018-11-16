from rest_framework import serializers

from surf.apps.filters import models


class FilterCategoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FilterCategoryItem
        fields = ('id', 'external_id', 'title',)


class FilterCategorySerializer(serializers.ModelSerializer):
    external_id = serializers.CharField(source="edurep_field_id")
    items = FilterCategoryItemSerializer(many=True)

    class Meta:
        model = models.FilterCategory
        fields = ('id', 'external_id', 'title', 'items',)


class FilterItemSerializer(serializers.ModelSerializer):
    category_item_id = serializers.CharField(source="category_item.id")

    category_id = serializers.CharField(source="category_item.category.id",
                                        read_only=True)

    class Meta:
        model = models.FilterCategoryItem
        fields = ('id', 'category_item_id', 'category_id',)


class FilterSerializer(serializers.ModelSerializer):
    items = FilterItemSerializer(many=True, required=False)

    def create(self, validated_data):
        request = self.context.get("request")
        if not request:
            raise TypeError("Invalid user")

        user = request.user
        if not user or not user.is_authenticated:
            raise TypeError("Invalid user")

        validated_data["owner_id"] = user.id
        validated_data.pop("items", None)
        rv = super().create(validated_data)

        for it in self.initial_data.get("items", []):
            rv.items.create(category_item_id=it["category_item_id"])

        return rv

    def update(self, instance, validated_data):
        validated_data.pop("items", None)
        instance = super().update(instance, validated_data)

        if "items" in self.initial_data:
            instance.items.all().delete()
            for it in self.initial_data.get("items", []):
                instance.items.create(category_item_id=it["category_item_id"])

        return instance

    class Meta:
        model = models.Filter
        fields = ('id', 'title', 'items', 'start_date', 'end_date',)
