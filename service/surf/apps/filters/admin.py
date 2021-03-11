"""
This module provides django admin functionality for filters app.
"""

from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from surf.apps.filters import models


@admin.register(models.MpttFilterItem)
class MpttFilterItemAdmin(DraggableMPTTAdmin):

    search_fields = ('name', 'external_id',)
    list_display = ('tree_actions', 'indented_title', 'is_hidden', 'is_manual',)
    list_display_links = ('indented_title',)
