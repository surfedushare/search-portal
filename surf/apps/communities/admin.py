from django.contrib import admin

from surf.apps.communities import models


@admin.register(models.Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ("external_id", "name", "description", "is_available",)
    list_filter = ("is_available",)
