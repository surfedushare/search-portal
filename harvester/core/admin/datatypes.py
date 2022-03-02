from django.contrib import admin

from datagrowth.admin import DataStorageAdmin, DocumentAdmin as DatagrowthDocumentAdmin
from core.admin.harvest import HarvestAdminInline
from core.admin.filters import TrashListFilter


class DatasetAdmin(DataStorageAdmin):
    inlines = [HarvestAdminInline]


class DatasetVersionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_current', "created_at")


class DocumentAdmin(DatagrowthDocumentAdmin):
    list_display = ['__str__', 'reference', 'dataset_version', 'collection', 'created_at', 'modified_at']
    list_filter = ('dataset_version',)
    readonly_fields = ("created_at", "modified_at",)


def trash_extensions(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()


def restore_extensions(modeladmin, request, queryset):
    for obj in queryset:
        obj.restore()


trash_extensions.short_description = "Trash selected %(verbose_name_plural)s"
restore_extensions.short_description = "Restore selected %(verbose_name_plural)s"


class ExtensionAdmin(DocumentAdmin):
    list_display = ['__str__', 'reference', 'dataset_version', 'collection', 'created_at', 'modified_at', 'deleted_at']
    list_filter = ('dataset_version', TrashListFilter)
    readonly_fields = ("created_at", "modified_at", "deleted_at",)

    actions = [trash_extensions, restore_extensions]

    def get_actions(self, request):
        actions = super().get_actions(request)
        try:
            filter_trash = bool(int(request.GET.get('trash', '0')))
        except ValueError:
            filter_trash = False
        if filter_trash:
            if "trash_extensions" in actions.keys():
                del actions["trash_extensions"]
        else:
            if "delete_selected" in actions.keys():
                del actions["delete_selected"]
            if "restore_extensions" in actions.keys():
                del actions["restore_extensions"]
        return actions
