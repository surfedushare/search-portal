from rest_framework import serializers
from surf.apps.localeHTML.models import LocaleHTML


class LocaleHTMLSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocaleHTML
        fields = ('en', 'nl',)
