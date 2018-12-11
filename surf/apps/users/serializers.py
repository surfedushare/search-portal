"""
This module contains API view serializers for users app.
"""

from rest_framework import serializers

from surf.apps.users.models import User


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User profile instance serializer
    """

    full_name = serializers.CharField(source="surfconext_auth.display_name")

    class Meta:
        model = User
        fields = ('id', 'full_name',)
