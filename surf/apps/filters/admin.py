from django.contrib import admin

from surf.apps.filters import models
from surf.apps.filters.utils import update_filter_category


@admin.register(models.Filter)
class FilterAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", )
    ordering = ("title",)


@admin.register(models.FilterItem)
class FilterItemAdmin(admin.ModelAdmin):
    list_display = ("filter", "category_item", )
    ordering = ("filter__title", "category_item__title", )
    list_filter = ("filter",)


def fill_filter_category(modeladmin, request, queryset):
    for fc in queryset.all():
        update_filter_category(fc)
fill_filter_category.short_description = "Fill filter category items"


@admin.register(models.FilterCategory)
class FilterCategoryAdmin(admin.ModelAdmin):
    actions = [fill_filter_category]

    list_display = ("title", "edurep_field_id", "max_item_count", )
    ordering = ("title", )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'restore_invoices' in actions:
                del actions['restore_invoices']
            if 'set_invoice_amounts' in actions:
                del actions['set_invoice_amounts']
            if 'validate_order_countries' in actions:
                del actions['validate_order_countries']
        return actions


@admin.register(models.FilterCategoryItem)
class FilterCategoryItemAdmin(admin.ModelAdmin):
    list_display = ("title", "external_id", "category", )
    ordering = ("title", )
    list_filter = ("category",)
