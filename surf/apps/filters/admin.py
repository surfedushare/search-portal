from django.contrib import admin

from surf.apps.filters import models


@admin.register(models.Filter)
class FilterAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", )
    ordering = ("title",)


@admin.register(models.FilterItem)
class FilterItemAdmin(admin.ModelAdmin):
    list_display = ("filter", "category_item", )
    ordering = ("filter__title", "category_item__title", )
    list_filter = ("filter",)


@admin.register(models.FilterCategory)
class FilterCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "edurep_field_id", "max_item_count", )
    ordering = ("title", )


@admin.register(models.FilterCategoryItem)
class FilterCategoryItemAdmin(admin.ModelAdmin):
    list_display = ("title", "external_id", "category", )
    ordering = ("title", )
    list_filter = ("category",)
