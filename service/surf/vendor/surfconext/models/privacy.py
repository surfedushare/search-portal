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

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    modified_at = models.DateTimeField(_("modified at"), auto_now=True)

    def get_default_privacy_settings(self):
        return [
            {
                "is_allowed": None,
                "type": goal.type,
                "en": {
                    "title": goal.en_title,
                    "description": goal.en_description,
                },
                "nl": {
                    "title": goal.nl_title,
                    "description": goal.nl_description,
                },
                "more_info_route": goal.more_info_route,
                "priority": goal.priority,
                "is_after_login": goal.is_after_login,
                "is_notification_only": goal.is_notification_only
            }
            for goal in self.datagoal_set.filter(is_active=True)
        ]

    def add_default_privacy_settings(self, input_permissions, default_permissions=None):
        default_permissions = default_permissions or self.get_default_privacy_settings()
        permissions_by_type = {permission["type"]: permission for permission in input_permissions}
        permissions = []
        for permission in default_permissions:
            if permission["type"] in permissions_by_type:
                permissions.append(permissions_by_type[permission["type"]])
            else:
                permissions.append(permission)
        return permissions

    def get_privacy_settings(self, user=None, session_permissions=None):
        # We'll assume session permissions are in order possibly enhanced by default permissions
        session_permissions = session_permissions or []
        permissions = self.add_default_privacy_settings(session_permissions)
        # When not dealing with an authenticated user we return "not allowed" for all goals
        if user is None or user.is_anonymous:
            return permissions
        # Here we're dealing with a specific user.
        # We'll return the settings for that user.
        # Or the defaults if any are missing.
        user_permissions_objects = list(DataGoalPermission.objects.filter(user=user))
        if not len(user_permissions_objects):
            return permissions
        # We take the permissions from the account
        # If any are missing we'll use the permissions from session/default
        serializer = DataGoalPermissionSerializer(user_permissions_objects, many=True)
        return self.add_default_privacy_settings(serializer.data, permissions)

    class Meta:
        ordering = ("created_at",)


class DataGoalPermission(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goal = models.ForeignKey("DataGoal", on_delete=models.CASCADE)

    recorded_at = models.DateTimeField(_("recorded at"), auto_now=True)
    is_allowed = models.NullBooleanField(_("is allowed"), )
    is_retained = models.BooleanField(_("is retained"), default=False)


class DataGoal(models.Model):

    statement = models.ForeignKey(PrivacyStatement, on_delete=models.CASCADE)
    en_title = models.CharField(_("english title"), max_length=256)
    nl_title = models.CharField(_("dutch title"), max_length=256)
    en_description = models.CharField(_("english description"), max_length=256)
    nl_description = models.CharField(_("dutch description"), max_length=256)
    more_info_route = models.CharField(_("more info route"), max_length=50)

    is_active = models.BooleanField(_("is active"), default=False)
    type = models.CharField(_("type"), choices=DATA_GOAL_TYPE_CHOICES, max_length=50)
    priority = models.SmallIntegerField(_("priority"), )
    is_notification_only = models.BooleanField(_("is notification only"), default=False)
    is_after_login = models.BooleanField(_("is after login"), default=False)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through=DataGoalPermission, verbose_name=_(""))

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    modified_at = models.DateTimeField(_("modified at"), auto_now=True)

    class Meta:
        ordering = ("created_at", "-priority",)


class DataGoalPermissionListSerializer(serializers.ListSerializer):

    def create(self, validated_data):
        user = self.context["user"]
        if user.is_anonymous:
            raise AuthenticationFailed("Can't permanently store data goal permissions for anonymous users")
        goal = DataGoal.objects.get(type=validated_data["type"], is_active=True)
        permission, created = DataGoalPermission.objects.update_or_create(
            user=user,
            goal=goal,
            defaults={"is_allowed": validated_data["is_allowed"]}
        )
        return permission


class DataGoalPermissionSerializer(serializers.ModelSerializer):

    type = serializers.ChoiceField(source="goal.type", choices=DATA_GOAL_TYPE_CHOICES)
    priority = serializers.IntegerField(source="goal.priority", required=False)
    en = serializers.SerializerMethodField()
    nl = serializers.SerializerMethodField()
    more_info_route = serializers.CharField(source="goal.more_info_route", max_length=50)
    is_notification_only = serializers.BooleanField(source="goal.is_notification_only", required=False)
    is_after_login = serializers.BooleanField(source="goal.is_after_login", required=False)

    def get_en(self, obj):
        return {
            "title": obj.goal.en_title,
            "description": obj.goal.en_description
        }

    def get_nl(self, obj):
        return {
            "title": obj.goal.nl_title,
            "description": obj.goal.nl_description
        }

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        en_translations = data.get("en", {})
        nl_translations = data.get("nl", {})
        internal_value.update({
            "en": en_translations,
            "nl": nl_translations
        })
        return internal_value

    class Meta:
        model = DataGoalPermission
        list_serializer_class = DataGoalPermissionListSerializer
        fields = ("id", "type", "en", "nl", "more_info_route", "priority",
                  "is_notification_only", "is_after_login", "is_allowed")
        read_only_fields = ("en", "nl", "more_info_route", "priority", "is_notification_only", "is_after_login")
