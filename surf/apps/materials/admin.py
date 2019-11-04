"""
This module provides django admin functionality for materials app.
"""

from django.contrib import admin


from surf.apps.materials import models
from surf.apps.materials.utils import update_materials_data


def trash_nodes(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()


trash_nodes.short_description = "Trash selected %(verbose_name_plural)s"


def restore_nodes(modeladmin, request, queryset):
    for obj in queryset:
        obj.restore()


restore_nodes.short_description = "Restore selected %(verbose_name_plural)s"


class TrashListFilter(admin.SimpleListFilter):

    title = 'is trash'
    parameter_name = 'trash'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Yes'),
            ('0', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value() or '0'
        try:
            is_trash = bool(int(value))
        except ValueError:
            is_trash = False
        return queryset.filter(deleted_at__isnull=not is_trash)


@admin.register(models.Material)
class MaterialAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for Material model.
    """

    list_display = ("title", "external_id")
    list_filter = (TrashListFilter,)
    readonly_fields = (
        'external_id', 'themes', 'disciplines', 'material_url', 'title',
        'description', 'keywords', "deleted_at",
    )
    actions = [restore_nodes, trash_nodes]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            # remove "only for admin" actions
            actions.pop('fill_material_data', None)
        try:
            filter_trash = bool(int(request.GET.get('trash', '0')))
        except ValueError:
            filter_trash = False
        if filter_trash:
            del actions["trash_nodes"]
        else:
            del actions["delete_selected"]
            del actions["restore_nodes"]
        return actions


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for Collection model.
    """

    list_display = ("title", "owner", "publish_status",)
    list_filter = ("owner", "publish_status",)
    readonly_fields = ('title', 'owner', "deleted_at",)
    ordering = ("title",)
    actions = [restore_nodes, trash_nodes]

    def get_actions(self, request):
        actions = super().get_actions(request)
        try:
            filter_trash = bool(int(request.GET.get('trash', '0')))
        except ValueError:
            filter_trash = False
        if filter_trash:
            del actions["trash_nodes"]
        else:
            del actions["delete_selected"]
            del actions["restore_nodes"]
        return actions
