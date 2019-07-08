"""
This module provides django admin functionality for materials app.
"""

from django.contrib import admin

from surf.apps.materials import models
from surf.apps.materials.utils import update_materials_data


def fill_material_data(model_admin, request, queryset):
    update_materials_data(queryset.all())


fill_material_data.short_description = "Fill material data"


@admin.register(models.Material)
class MaterialAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for Material model.
    """

    actions = [fill_material_data]
    readonly_fields = (
        'external_id', 'themes', 'disciplines', 'material_url', 'title',
        'description', 'keywords'
    )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            # remove "only for admin" actions
            actions.pop('fill_material_data', None)
        return actions


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for Collection model.
    """

    list_display = ("title", "owner", "is_shared",)
    list_filter = ("owner", "is_shared",)
    readonly_fields = ('title', 'owner', 'materials', 'is_shared',)
    ordering = ("title",)
