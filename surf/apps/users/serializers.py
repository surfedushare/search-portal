from rest_framework import serializers

from surf.apps.users.models import User


class UserDetailsSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="surfconext_auth.display_name")

    class Meta:
        model = User
        fields = ('id', 'full_name',)
