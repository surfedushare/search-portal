from django.contrib import admin

from datagrowth.admin import HttpResourceAdmin
from sources.models import (HanOAIPMHResource, HvaPureResource, HkuMetadataResource, GreeniOAIPMHResource,
                            BuasPureResource, HanzeResearchObjectResource, PublinovaMetadataResource)


admin.site.register(HanOAIPMHResource, HttpResourceAdmin)
admin.site.register(HvaPureResource, HttpResourceAdmin)
admin.site.register(HkuMetadataResource, HttpResourceAdmin)
admin.site.register(GreeniOAIPMHResource, HttpResourceAdmin)
admin.site.register(BuasPureResource, HttpResourceAdmin)
admin.site.register(HanzeResearchObjectResource, HttpResourceAdmin)
admin.site.register(PublinovaMetadataResource, HttpResourceAdmin)
