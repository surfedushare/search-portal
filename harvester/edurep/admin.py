from django.contrib import admin

from datagrowth.admin import HttpResourceAdmin
from edurep.models import EdurepOAIPMH


admin.site.register(EdurepOAIPMH, HttpResourceAdmin)
