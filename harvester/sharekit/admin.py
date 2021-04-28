from django.contrib import admin

from datagrowth.admin import HttpResourceAdmin
from sharekit.models import SharekitMetadataHarvest


admin.site.register(SharekitMetadataHarvest, HttpResourceAdmin)
