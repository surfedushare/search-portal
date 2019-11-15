from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed


class DataGoalTypes:
    COOKIES = "Cookies"
    COMMUNITIES = "Communities"
    RECOMMENDATIONS = "Recommendations"


DATA_GOAL_TYPE_CHOICES = [
    (value, value) for attr, value in sorted(DataGoalTypes.__dict__.items()) if not attr.startswith("_")
]


class PrivacyStatementManager(models.Manager):

    def get_latest_active(self):
        return super().get_queryset().filter(is_active=True).last()


class PrivacyStatement(models.Model):

    objects = PrivacyStatementManager()

    name = models.CharField(_("name"), max_length=50)
    is_active = models.BooleanField(_("is active"), default=False)

    en = models.TextField(_("english"))
    nl = models.TextField(_("dutch"))

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_privacy_settings(self, user=None):
        # When not dealing with an authenticated user we return "not allowed" for all goals
        if user is None or user.is_anonymous:
            return [
                {
                    "is_allowed": False,
                    "type": goal.type,
                    "priority": goal.priority,
                    "is_after_login": goal.is_after_login,
                    "is_notification_only": goal.is_notification_only
                }
                for goal in self.datagoal_set.filter(is_active=True)
            ]
        # Here we're dealing with a specific user. We'll return the settings for that user.
        print("authenticated??")

    class Meta:
        ordering = ("created_at",)


class DataGoalPermission(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goal = models.ForeignKey("DataGoal", on_delete=models.CASCADE)

    recorded_at = models.DateTimeField(auto_now=True)
    is_allowed = models.NullBooleanField()
    is_retained = models.BooleanField(default=False)


class DataGoal(models.Model):

    statement = models.ForeignKey(PrivacyStatement, on_delete=models.CASCADE)
    en = models.CharField(_("english"), max_length=256)
    nl = models.CharField(_("dutch"), max_length=256)

    is_active = models.BooleanField(default=False)
    type = models.CharField(choices=DATA_GOAL_TYPE_CHOICES, max_length=50)
    priority = models.SmallIntegerField()
    is_notification_only = models.BooleanField(default=False)
    is_after_login = models.BooleanField(default=False)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through=DataGoalPermission)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("created_at", "-priority",)


class DataGoalPermissionListSerializer(serializers.ListSerializer):

    def create(self, validated_data):
        user = self.context["request"].user
        if user.is_anonymous:
            raise AuthenticationFailed("Can't permanently store data goal permissions for anonymous users")
        permission, created = DataGoalPermission.objects.update_or_create(
            user=user,
            goal__type=validated_data["type"],
            defaults={"is_allowed": validated_data["is_allowed"]}
        )
        return permission


class DataGoalPermissionSerializer(serializers.ModelSerializer):

    type = serializers.ChoiceField(source="goal.type", choices=DATA_GOAL_TYPE_CHOICES)
    priority = serializers.IntegerField(source="goal.priority", required=False)
    is_notification_only = serializers.BooleanField(source="goal.is_notification_only", required=False)
    is_after_login = serializers.BooleanField(source="goal.is_after_login", required=False)

    class Meta:
        model = DataGoalPermission
        list_serializer_class = DataGoalPermissionListSerializer
        fields = ("id", "type", "priority", "is_notification_only", "is_after_login", "is_allowed")
        read_only_fields = ("priority", "is_notification_only", "is_after_login")
