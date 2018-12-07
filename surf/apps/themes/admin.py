"""
This module provides django admin functionality for themes app.
"""

from django import forms
from django.contrib import admin

from surf.apps.themes import models
from surf.apps.filters.models import FilterCategoryItem

from surf.vendor.edurep.xml_endpoint.v1_2.api import (
    CUSTOM_THEME_FIELD_ID,
    DISCIPLINE_FIELD_ID
)


class ThemeForm(forms.ModelForm):
    """
    Implementation of Theme Form class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            qs = FilterCategoryItem.objects

            # choose only Theme filter category items
            t_qs = qs.filter(category__edurep_field_id=CUSTOM_THEME_FIELD_ID)
            self.fields['filter_category_item'].queryset = t_qs.all()

            # choose only Discipline filter category items
            d_qs = qs.filter(category__edurep_field_id=DISCIPLINE_FIELD_ID)
            self.fields['disciplines'].queryset = d_qs.all()
        except AttributeError:
            pass

    class Meta:
        model = models.Theme
        fields = '__all__'


@admin.register(models.Theme)
class ThemeAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for Theme model.
    """

    form = ThemeForm
