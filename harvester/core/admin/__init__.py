from django.conf import settings
from django.contrib import admin

from datagrowth.admin import DataStorageAdmin, HttpResourceAdmin, ShellResourceAdmin

from core.models import (Dataset, DatasetVersion, Collection, Document, HarvestSource, HttpTikaResource, ElasticIndex,
                         ExtructResource, YoutubeThumbnailResource, ExtractionMapping, ExtractionMethod,
                         JSONExtractionField, MethodExtractionField)
from core.admin.datatypes import DatasetAdmin, DatasetVersionAdmin, ExtendedDocumentAdmin
from core.admin.harvest import HarvestSourceAdmin
from core.admin.search import ElasticIndexAdmin
from core.admin.extraction import ExtractionMappingAdmin, ExtractionMethodAdmin


admin.site.register(HarvestSource, HarvestSourceAdmin)
admin.site.register(HttpTikaResource, HttpResourceAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(DatasetVersion, DatasetVersionAdmin)
admin.site.register(Collection, DataStorageAdmin)
admin.site.register(Document, ExtendedDocumentAdmin)
admin.site.register(ElasticIndex, ElasticIndexAdmin)
admin.site.register(ExtructResource, HttpResourceAdmin)
admin.site.register(YoutubeThumbnailResource, ShellResourceAdmin)

if settings.PROJECT == "nppo":
    admin.site.register(ExtractionMapping, ExtractionMappingAdmin)
    admin.site.register(ExtractionMethod, ExtractionMethodAdmin)
    admin.site.register(JSONExtractionField, admin.ModelAdmin)
    admin.site.register(MethodExtractionField, admin.ModelAdmin)
