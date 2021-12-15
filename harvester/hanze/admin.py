from django.contrib import admin
from datagrowth.admin import HttpResourceAdmin

from hanze.models import HanzeResearchObjectResource


admin.site.register(HanzeResearchObjectResource, HttpResourceAdmin)
