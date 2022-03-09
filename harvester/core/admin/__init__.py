from django.conf import settings
from django.contrib import admin

from datagrowth.admin import DataStorageAdmin, HttpResourceAdmin, ShellResourceAdmin

from core.models import (Dataset, DatasetVersion, Collection, Document, HarvestSource, HttpTikaResource, ElasticIndex,
                         ExtructResource, YoutubeThumbnailResource, ExtractionMapping, ExtractionMethod,
                         JSONExtractionField, MethodExtractionField, PdfThumbnailResource, Query, Extension,
                         MatomoVisitsResource)
from core.admin.datatypes import DatasetAdmin, DatasetVersionAdmin, DocumentAdmin, ExtensionAdmin
from core.admin.harvest import HarvestSourceAdmin
from core.admin.search import ElasticIndexAdmin
from core.admin.extraction import ExtractionMappingAdmin, ExtractionMethodAdmin
from core.admin.query import QueryAdmin


admin.site.register(HarvestSource, HarvestSourceAdmin)
admin.site.register(HttpTikaResource, HttpResourceAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(DatasetVersion, DatasetVersionAdmin)
admin.site.register(Collection, DataStorageAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(ElasticIndex, ElasticIndexAdmin)
admin.site.register(ExtructResource, HttpResourceAdmin)
admin.site.register(MatomoVisitsResource, HttpResourceAdmin)

if settings.PROJECT == "nppo":
    admin.site.register(ExtractionMapping, ExtractionMappingAdmin)
    admin.site.register(ExtractionMethod, ExtractionMethodAdmin)
    admin.site.register(JSONExtractionField, admin.ModelAdmin)
    admin.site.register(MethodExtractionField, admin.ModelAdmin)
    admin.site.register(Extension, ExtensionAdmin)
else:
    admin.site.register(YoutubeThumbnailResource, ShellResourceAdmin)
    admin.site.register(PdfThumbnailResource, HttpResourceAdmin)
    admin.site.register(Query, QueryAdmin)
