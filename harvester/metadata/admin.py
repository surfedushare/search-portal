from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from mptt.admin import DraggableMPTTAdmin

from metadata.models import MetadataValue, MetadataField, MetadataTranslation


class MetadataFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_hidden', 'is_manual', 'english_as_dutch',)


class MetadataTranslationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'nl', 'en', 'is_fuzzy', 'change_metadata_value')
    list_editable = ('nl', 'en', 'is_fuzzy',)
    list_filter = ('is_fuzzy',)
    search_fields = ('en', 'nl',)

    def change_metadata_value(self, obj):
        button_label = "metadata"
        url = reverse("admin:metadata_metadatavalue_change", args=(obj.metadatavalue.id,))
        return format_html('<a class="button" href="{}">{}</a>', url, button_label)


def unhide_filters(modeladmin, request, queryset):
    for obj in queryset:
        for descendent in obj.get_descendants():
            descendent.is_hidden = False
            descendent.save()
        obj.is_hidden = False
        obj.save()


def trash_nodes(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()


def restore_nodes(modeladmin, request, queryset):
    for obj in queryset:
        obj.restore()


unhide_filters.short_description = "Unhide all selected filters and its descendents"
trash_nodes.short_description = "Trash selected %(verbose_name_plural)s"
restore_nodes.short_description = "Restore selected %(verbose_name_plural)s"


class TrashListFilter(admin.SimpleListFilter):

    title = 'is trash'
    parameter_name = 'trash'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Yes'),
            ('0', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value() or '0'
        try:
            is_trash = bool(int(value))
        except ValueError:
            is_trash = False
        return queryset.filter(deleted_at__isnull=not is_trash)


class MetadataValueAdmin(DraggableMPTTAdmin):

    search_fields = ('name', 'value',)
    autocomplete_fields = ("translation", "parent",)
    list_display = ('tree_actions', 'indented_title', 'is_hidden', 'is_manual', 'frequency', 'deleted_at',)
    list_display_links = ('indented_title',)
    list_filter = ('is_hidden', 'field', TrashListFilter)
    readonly_fields = ('frequency', 'deleted_at', 'value',)

    actions = [unhide_filters, trash_nodes, restore_nodes]

    def get_actions(self, request):
        actions = super().get_actions(request)
        try:
            filter_trash = bool(int(request.GET.get('trash', '0')))
        except ValueError:
            filter_trash = False
        if filter_trash:
            if "trash_nodes" in actions.keys():
                del actions["trash_nodes"]
        else:
            if "delete_selected" in actions.keys():
                del actions["delete_selected"]
            if "restore_nodes" in actions.keys():
                del actions["restore_nodes"]
        return actions


admin.site.register(MetadataValue, MetadataValueAdmin)
admin.site.register(MetadataField, MetadataFieldAdmin)
admin.site.register(MetadataTranslation, MetadataTranslationAdmin)
