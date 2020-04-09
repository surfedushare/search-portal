
from django.contrib import admin
from surf.apps.querylog import models


@admin.register(models.QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "search_text", "result_size")
