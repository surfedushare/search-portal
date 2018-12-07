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

    list_display = ("external_id", "name", "description", "is_available",)
    list_filter = ("is_available",)
