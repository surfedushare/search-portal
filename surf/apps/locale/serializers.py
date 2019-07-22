from rest_framework import serializers
from surf.apps.locale.models import Locale


class LocaleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Locale
        fields = ('en', 'nl',)
