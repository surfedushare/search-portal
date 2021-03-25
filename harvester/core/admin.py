from django.contrib import admin
from django.contrib import messages

from datagrowth.admin import DataStorageAdmin, DocumentAdmin, HttpResourceAdmin, ShellResourceAdmin

from core.models import (Dataset, Collection, Arrangement, Document, HarvestSource, ElasticIndex, CommonCartridge,
                         FileResource, TikaResource)


class HarvestSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "spec", "created_at", "modified_at",)


class HarvestAdminInline(admin.TabularInline):
    model = HarvestSource.datasets.through
    fields = ("source", "harvested_at", "latest_update_at", "stage",)
    readonly_fields = ("harvested_at",)
    extra = 0


class DatasetAdmin(DataStorageAdmin):
    inlines = [HarvestAdminInline]

    actions = ["reset_dataset_harvest"]

    def reset_dataset_harvest(self, request, queryset):
        """
        Convenience method to reset dataset harvests from the admin interface
        """
        for dataset in queryset:
            dataset.reset()
        messages.success(request, f"{queryset.count()} datasets reset to harvest from 01-01-1970")


class ArrangementAdmin(DataStorageAdmin):
    search_fields = ["meta"]


class ExtendedDocumentAdmin(DocumentAdmin):
    list_display = ['__str__', 'dataset', 'collection', 'arrangement', 'created_at', 'modified_at']
    list_filter = ('dataset', 'collection',)


class ElasticIndexAdmin(admin.ModelAdmin):
    list_display = ("name", "remote_name", "remote_exists", "error_count", "language", "created_at", "modified_at",)


class CommonCartridgeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'upload_at', 'metadata_tag')


admin.site.register(HarvestSource, HarvestSourceAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Collection, DataStorageAdmin)
admin.site.register(Arrangement, ArrangementAdmin)
admin.site.register(Document, ExtendedDocumentAdmin)
admin.site.register(ElasticIndex, ElasticIndexAdmin)
admin.site.register(CommonCartridge, CommonCartridgeAdmin)
admin.site.register(FileResource, HttpResourceAdmin)
admin.site.register(TikaResource, ShellResourceAdmin)
