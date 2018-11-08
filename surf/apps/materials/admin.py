from django.contrib import admin

from surf.apps.materials import models


@admin.register(models.Material)
class MaterialAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", )
    ordering = ("title",)


@admin.register(models.ApplaudMaterial)
class ApplaudMaterialAdmin(admin.ModelAdmin):
    list_display = ("material", "user", )
    ordering = ("material", "user", )
    list_filter = ("material", "user", )


@admin.register(models.ViewMaterial)
class ViewMaterialAdmin(admin.ModelAdmin):
    list_display = ("material", "user", )
    ordering = ("material", "user", )
    list_filter = ("material", "user", )
