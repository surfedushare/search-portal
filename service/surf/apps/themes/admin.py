from django.conf import settings
from django.contrib import admin

from surf.apps.themes.models import Theme


class ThemeAdmin(admin.ModelAdmin):
    list_display = ('nl_slug', 'en_slug', 'external_id',)


if settings.PROJECT == "edusources":
    admin.site.register(Theme, ThemeAdmin)
