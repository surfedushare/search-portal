from django.contrib import admin

from surf.apps.materials import models


@admin.register(models.Material)
class MaterialAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", )
    ordering = ("title",)
