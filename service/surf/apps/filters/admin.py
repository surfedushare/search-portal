"""
This module provides django admin functionality for filters app.
"""

from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from surf.apps.filters import models


def unhide_filters(modeladmin, request, queryset):
    for obj in queryset:
        for descendent in obj.get_descendants():
            descendent.is_hidden = False
            descendent.save()
        obj.is_hidden = False
        obj.save()


unhide_filters.short_description = "Unhide all selected filters and its descendents"


@admin.register(models.MpttFilterItem)
class MpttFilterItemAdmin(DraggableMPTTAdmin):

    search_fields = ('name', 'external_id',)
    raw_id_fields = ("title_translations", "parent",)
    list_display = ('tree_actions', 'indented_title', 'is_hidden', 'is_manual',)
    list_display_links = ('indented_title',)
    list_filter = ('is_hidden',)

    actions = [unhide_filters]
