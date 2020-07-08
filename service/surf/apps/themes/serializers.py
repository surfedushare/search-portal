"""
This module contains API view serializers for themes app.
"""
from collections import OrderedDict

from rest_framework import serializers

from surf.apps.themes.models import Theme
from surf.apps.filters.models import MpttFilterItem
from surf.apps.locale.serializers import LocaleSerializer, LocaleHTMLSerializer
from surf.apps.filters.serializers import MpttFilterItemSerializer
from surf.vendor.elasticsearch.api import ElasticSearchApiClient


class ThemeSerializer(serializers.ModelSerializer):
    """
    Theme instance serializer
    """

    id = serializers.UUIDField(source="filter_category_item.id")
    title = serializers.CharField(source="filter_category_item.name")
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
        if obj.external_id:
            elastic = ElasticSearchApiClient()
            filters = [OrderedDict(external_id=obj.parent.external_id, items=[obj.external_id])]
            res = elastic.search([], filters=filters, page_size=0)
            return res['recordcount']

        return 0

    class Meta:
        model = MpttFilterItem
        fields = '__all__'
