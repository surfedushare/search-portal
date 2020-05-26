from django.contrib import admin

from datagrowth.admin import DataStorageAdmin, DocumentAdmin

from core.models import Dataset, Collection, Arrangement, Document, OAIPMHSet, ElasticIndex, CommonCartridge


class OAIPMHSetAdmin(admin.ModelAdmin):
    list_display = ("name", "spec", "created_at", "modified_at",)


class OAIPMHHarvestAdminInline(admin.TabularInline):
    model = OAIPMHSet.datasets.through
    fields = ("source", "harvested_at", "latest_update_at", "stage",)
    readonly_fields = ("harvested_at",)
    extra = 0


class DatasetAdmin(DataStorageAdmin):
    inlines = [OAIPMHHarvestAdminInline]


class ExtendedDocumentAdmin(DocumentAdmin):
    list_display = ['__str__', 'dataset', 'collection', 'arrangement', 'created_at', 'modified_at']
    list_filter = ('dataset', 'collection',)


class ElasticIndexAdmin(admin.ModelAdmin):
    list_display = ("name", "remote_name", "remote_exists", "error_count", "language", "created_at", "modified_at",)


class CommonCartridgeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'upload_at', 'metadata_tag')


admin.site.register(OAIPMHSet, OAIPMHSetAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Collection, DataStorageAdmin)
admin.site.register(Arrangement, DataStorageAdmin)
admin.site.register(Document, ExtendedDocumentAdmin)
admin.site.register(ElasticIndex, ElasticIndexAdmin)
admin.site.register(CommonCartridge, CommonCartridgeAdmin)
