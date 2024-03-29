from rest_framework import serializers

from surf.apps.locale.serializers import LocaleSerializer


class MpttFilterItemSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    parent = serializers.IntegerField()
    name = serializers.CharField(source="translation.nl")
    field = serializers.CharField()
    value = serializers.CharField()
    external_id = serializers.CharField(source="value")
    children = serializers.SerializerMethodField()
    title_translations = LocaleSerializer(source="translation")
    translation = LocaleSerializer()
    frequency = serializers.IntegerField()
    count = serializers.SerializerMethodField()
    is_hidden = serializers.BooleanField()

    def get_children(self, obj):
        return MpttFilterItemSerializer(
            obj["children"],
            many=True,
            context={
                "drilldowns": self.context.get("drilldowns", {})
            }
        ).data

    def get_count(self, obj):
        drilldowns = self.context.get('drilldowns', {})
        if not drilldowns:
            return obj["frequency"]
        return drilldowns.get(f"{obj['field']}-{obj['value']}", 0)

    class Meta:
        fields = ('id', 'name', 'parent', 'title_translations', 'translation', 'value', 'external_id', 'is_hidden',
                  'children', 'count', 'frequency', 'field')
