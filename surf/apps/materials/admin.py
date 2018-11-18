from django.contrib import admin
from django import forms

from surf.apps.materials import models
from surf.apps.filters.models import FilterCategoryItem
from surf.vendor.edurep.xml_endpoint.v1_2.api import DISCIPLINE_FIELD_ID


class MaterialForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            qs = FilterCategoryItem.objects
            qs = qs.filter(category__edurep_field_id=DISCIPLINE_FIELD_ID)
            self.fields['disciplines'].queryset = qs.all()
        except AttributeError:
            pass

    class Meta:
        model = models.Theme
        fields = '__all__'


@admin.register(models.Material)
class MaterialAdmin(admin.ModelAdmin):
    form = MaterialForm


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "is_shared",)
    list_filter = ("owner", "is_shared",)
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
