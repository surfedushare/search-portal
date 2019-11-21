"""
This module provides django admin functionality for filters app.
"""

from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from surf.apps.filters import models


# @admin.register(models.Filter)
class FilterAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for Filter model.
    """

    list_display = ("title", "owner", )
    ordering = ("title",)


# @admin.register(models.FilterItem)
class FilterItemAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for FilterItem model.
    """

    list_display = ("filter", "mptt_category_item", )
    ordering = ("filter__title", "mptt_category_item__name", )
    list_filter = ("filter",)


@admin.register(models.MpttFilterItem)
class MpttFilterItemAdmin(DraggableMPTTAdmin):

    search_fields = ('name', 'external_id',)
    list_display = ('tree_actions', 'indented_title', 'enabled_by_default', 'is_hidden')
    list_display_links = ('indented_title',)
