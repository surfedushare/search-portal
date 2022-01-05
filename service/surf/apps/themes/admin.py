from django.contrib import admin

from surf.apps.themes.models import Theme


class ThemeAdmin(admin.ModelAdmin):
    list_display = ('nl_slug', 'en_slug', 'external_id',)


admin.site.register(Theme, ThemeAdmin)
