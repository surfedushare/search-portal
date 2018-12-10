"""
This module provides django admin functionality for communities app.
"""

from django.contrib import admin

from surf.apps.communities import models


@admin.register(models.Community)
class CommunityAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for Community model.
    """

    list_display = ("custom_name", "custom_description", "is_available",)
    list_filter = ("is_available",)
    exclude = ("external_id", "admins", "members",)

    def custom_name(self, obj):
        if obj.name:
            return obj.name
        else:
            return obj.surf_team.name

    def custom_description(self, obj):
        if obj.description:
            return obj.description
        else:
            return obj.surf_team.description

    custom_description.short_description = 'Description'


@admin.register(models.SurfTeam)
class SurfTeamAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for SURFconext Team model.
    """

    list_display = ("external_id", "name", "description",)
