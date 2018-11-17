from django import forms
from django.contrib import admin

from surf.apps.themes import models
from surf.apps.filters.models import FilterCategoryItem

from surf.vendor.edurep.xml_endpoint.v1_2.api import (
    CUSTOM_THEME_FIELD_ID,
    DISCIPLINE_FIELD_ID
)


class ThemeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            qs = FilterCategoryItem.objects

            t_qs = qs.filter(category__edurep_field_id=CUSTOM_THEME_FIELD_ID)
            self.fields['filter_category_item'].queryset = t_qs.all()

            d_qs = qs.filter(category__edurep_field_id=DISCIPLINE_FIELD_ID)
            self.fields['disciplines'].queryset = d_qs.all()
        except AttributeError:
            pass

    class Meta:
        model = models.Theme
        fields = '__all__'


@admin.register(models.Theme)
class ThemeAdmin(admin.ModelAdmin):
    form = ThemeForm
