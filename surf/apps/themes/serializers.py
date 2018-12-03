from rest_framework import serializers

from surf.apps.themes.models import Theme
from surf.apps.filters.models import FilterCategoryItem

from surf.apps.filters.serializers import FilterCategoryItemSerializer


class ThemeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="filter_category_item.id")
    title = serializers.CharField(source="filter_category_item.title")

    class Meta:
        model = Theme
        fields = ('id', 'external_id', 'title', 'description',)


class ThemeDisciplineSerializer(FilterCategoryItemSerializer):
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
        model = FilterCategoryItem
        fields = ('id', 'external_id', 'title', 'materials_count',)
