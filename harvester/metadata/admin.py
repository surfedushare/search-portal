from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from metadata.models import MetadataValue, MetadataField, MetadataTranslation


class MetadataFieldAdmin(admin.ModelAdmin):
    pass


class MetadataTranslationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'nl', 'en', 'is_fuzzy',)
    list_editable = ('nl', 'en', 'is_fuzzy',)
    list_filter = ('is_fuzzy',)
    search_fields = ('en', 'nl',)


def unhide_filters(modeladmin, request, queryset):
    for obj in queryset:
        for descendent in obj.get_descendants():
            descendent.is_hidden = False
            descendent.save()
        obj.is_hidden = False
        obj.save()


unhide_filters.short_description = "Unhide all selected filters and its descendents"


class MetadataValueAdmin(DraggableMPTTAdmin):

    search_fields = ('name', 'value',)
    autocomplete_fields = ("translation", "parent",)
    list_display = ('tree_actions', 'indented_title', 'is_hidden', 'is_manual',)
    list_display_links = ('indented_title',)
    list_filter = ('is_hidden', 'field',)

    actions = [unhide_filters]


admin.site.register(MetadataValue, MetadataValueAdmin)
admin.site.register(MetadataField, MetadataFieldAdmin)
admin.site.register(MetadataTranslation, MetadataTranslationAdmin)
