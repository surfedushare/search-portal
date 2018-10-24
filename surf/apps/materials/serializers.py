from rest_framework import serializers


class SearchFilterSerializer(serializers.Serializer):
    external_id = serializers.CharField()
    items = serializers.ListField(child=serializers.CharField())


class SearchRequestSerializer(serializers.Serializer):
    search_text = serializers.ListField(child=serializers.CharField())
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=5)
    return_records = serializers.BooleanField(required=False, default=True)
    return_filters = serializers.BooleanField(required=False, default=True)

    ordering = serializers.CharField(required=False, allow_blank=True,
                                     allow_null=True)

    author = serializers.CharField(required=False, allow_blank=True,
                                   allow_null=True)

    filters = serializers.ListField(child=SearchFilterSerializer(),
                                    required=False,
                                    allow_null=True)


class KeywordsSerializer(serializers.Serializer):
    query = serializers.CharField()
