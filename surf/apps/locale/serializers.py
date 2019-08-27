from rest_framework import serializers
from surf.apps.locale.models import Locale, LocaleHTML


class LocaleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Locale
        fields = ('en', 'nl',)


class LocaleHTMLSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocaleHTML
        fields = ('en', 'nl',)
