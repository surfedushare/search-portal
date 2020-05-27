from django.contrib import admin

from datagrowth.admin import HttpResourceAdmin
from edurep.models import EdurepFile, EdurepOAIPMH


admin.site.register(EdurepFile, HttpResourceAdmin)
admin.site.register(EdurepOAIPMH, HttpResourceAdmin)
