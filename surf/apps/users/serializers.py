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
    is_admin = serializers.SerializerMethodField()

    @staticmethod
    def get_is_admin(obj):
        if not obj.admin_teams:
            return False

        return obj.admin_teams.filter(community__isnull=False).exists()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'is_admin',)
