from django.contrib import admin

from surf.apps.themes.models import Theme


class ThemeAdmin(admin.ModelAdmin):
    list_display = ('external_id',)
    raw_id_fields = ('filter_category_item',)
    filter_horizontal = ('disciplines',)


admin.site.register(Theme, ThemeAdmin)
