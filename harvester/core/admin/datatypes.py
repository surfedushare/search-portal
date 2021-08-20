from django.contrib import admin

from datagrowth.admin import DataStorageAdmin, DocumentAdmin
from core.admin.harvest import HarvestAdminInline


class DatasetAdmin(DataStorageAdmin):
    inlines = [HarvestAdminInline]


class DatasetVersionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_current', "created_at")


class ExtendedDocumentAdmin(DocumentAdmin):
    list_display = ['__str__', 'reference', 'dataset_version', 'collection', 'created_at', 'modified_at']
    list_filter = ('dataset_version',)
    readonly_fields = ("created_at", "modified_at",)
