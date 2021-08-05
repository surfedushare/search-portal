from django.conf import settings
from django.contrib import admin

from surf.apps.materials import models


def trash_nodes(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()


def restore_nodes(modeladmin, request, queryset):
    for obj in queryset:
        obj.restore()


def sync_info_nodes(modeladmin, request, queryset):
    for obj in queryset:
        obj.sync_info()


trash_nodes.short_description = "Trash selected %(verbose_name_plural)s"
restore_nodes.short_description = "Restore selected %(verbose_name_plural)s"
sync_info_nodes.short_description = "Fill %(verbose_name)s data"


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


class CollectionMaterialInline(admin.TabularInline):
    model = models.CollectionMaterial
    extra = 0


class MaterialAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for Material model.
    """

    list_display = ('external_id', 'view_count', 'applaud_count', 'get_avg_star_rating', 'deleted_at',)
    list_filter = (TrashListFilter,)
    readonly_fields = (
        'external_id', 'themes', 'disciplines', 'view_count', 'applaud_count', 'get_avg_star_rating',
        'get_star_count', "deleted_at",
    )
    search_fields = ('external_id',)
    inlines = (CollectionMaterialInline,)
    exclude = ['star_1', 'star_2', 'star_3', 'star_4', 'star_5']
    actions = [restore_nodes, trash_nodes, sync_info_nodes]

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
            if "trash_nodes" in actions.keys():
                del actions["trash_nodes"]
        else:
            if "delete_selected" in actions.keys():
                del actions["delete_selected"]
            if "restore_nodes" in actions.keys():
                del actions["restore_nodes"]
        return actions


class CollectionAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for Collection model.
    """

    list_display = ("title_nl", "title_en", "publish_status",)
    list_filter = (TrashListFilter, "publish_status",)
    readonly_fields = ("deleted_at",)
    ordering = ("title_nl",)
    exclude = ["is_shared"]
    inlines = [CollectionMaterialInline]
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


if settings.PROJECT == "edusources":
    admin.register(models.Material, MaterialAdmin)
    admin.register(models.Collection, CollectionAdmin)
