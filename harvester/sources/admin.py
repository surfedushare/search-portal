from django.contrib import admin

from datagrowth.admin import HttpResourceAdmin
from sources.models import HanOAIPMHResource


admin.site.register(HanOAIPMHResource, HttpResourceAdmin)
