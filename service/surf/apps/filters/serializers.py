from rest_framework import serializers

from surf.apps.filters import models
from surf.apps.locale.serializers import LocaleSerializer


class MpttFilterItemSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()
    parent = serializers.IntegerField()
    name = serializers.CharField(source="translation.nl")
    field = serializers.CharField()
    value = serializers.CharField()
    external_id = serializers.CharField(source="value")
    children = serializers.SerializerMethodField()
    title_translations = LocaleSerializer(source="translation")
    translation = LocaleSerializer()
    frequency = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    def get_children(self, obj):
        return MpttFilterItemSerializer(
            obj["children"],
            many=True,
            context={
                "drilldowns": self.context.get("drilldowns", {})
            }
        ).data

    def get_count(self, obj):
        return self.get_frequency(obj)

    def get_frequency(self, obj):
        drilldowns = self.context.get('drilldowns', {})
        if not drilldowns:
            return obj["frequency"]
        return drilldowns.get(f"{obj['field']}-{obj['value']}", 0)

    class Meta:
        model = models.MpttFilterItem
        fields = ('id', 'name', 'parent', 'title_translations', 'translation', 'value', 'external_id', 'is_hidden',
                  'children', 'count', 'frequency', 'field')
