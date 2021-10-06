from django.contrib import admin

from datagrowth.admin import HttpResourceAdmin
from anatomy_tool.models import AnatomyToolOAIPMH


admin.site.register(AnatomyToolOAIPMH, HttpResourceAdmin)
