from rest_framework import serializers

from surf.apps.communities.models import Community


class CommunityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ('name', 'description', 'website_url',
                  'logo', 'featured_image',)


class CommunitySerializer(CommunityUpdateSerializer):
    members_count = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()

    @staticmethod
    def get_members_count(obj):
        return obj.members.count()

    def get_is_admin(self, obj):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            return obj.admins.filter(id=request.user.id).exists()
        return False

    def get_is_member(self, obj):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            return obj.members.filter(id=request.user.id).exists()
        return False

    class Meta:
        model = Community
        fields = ('id', 'external_id', 'name', 'description', 'website_url',
                  'logo', 'featured_image', 'members_count',
                  'is_admin', 'is_member',)
