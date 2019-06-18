"""
This module provides django admin functionality for materials app.
"""

from django.contrib import admin
from django import forms

from surf.apps.materials import models
from surf.apps.filters.models import FilterCategoryItem
from surf.apps.materials.utils import update_materials_data
from surf.vendor.edurep.xml_endpoint.v1_2.api import DISCIPLINE_FIELD_ID


class MaterialForm(forms.ModelForm):
    """
    Implementation of Material Form class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            # choose only Discipline filter category items
            qs = FilterCategoryItem.objects
            qs = qs.filter(category__edurep_field_id=DISCIPLINE_FIELD_ID)
            self.fields['disciplines'].queryset = qs.all()
        except AttributeError:
            pass

    class Meta:
        model = models.Theme
        fields = '__all__'


def fill_material_data(model_admin, request, queryset):
    update_materials_data(queryset.all())


fill_material_data.short_description = "Fill material data"


@admin.register(models.Material)
class MaterialAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for Material model.
    """

    actions = [fill_material_data]
    form = MaterialForm

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            # remove "only for admin" actions
            actions.pop('fill_material_data', None)
        return actions


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for Collection model.
    """

    list_display = ("title", "owner", "is_shared",)
    list_filter = ("owner", "is_shared",)
    ordering = ("title",)
