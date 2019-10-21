"""
This module provides django admin functionality for communities app.
"""

from django.contrib import admin
from django import forms
from django.db.models import Q
from django.core.files.images import get_image_dimensions

from surf.apps.communities import models


class CommunityForm(forms.ModelForm):
    """
    Implementation of Community Form class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_logo(self):
        picture = self.cleaned_data.get("logo")
        validate_image_proportion(picture, 230, 136)
        return picture

    def clean_featured_image(self):
        picture = self.cleaned_data.get("featured_image")
        validate_image_proportion(picture, 388, 227)
        return picture

    class Meta:
        model = models.Community
        fields = '__all__'


def validate_image_proportion(image, width, height):
    if not image:
        return

    w, h = get_image_dimensions(image)
    if w * height != h * width:
        raise forms.ValidationError(
            "The image proportion should be {}x{}!".format(width, height))


class TeamInline(admin.TabularInline):
    model = models.Team
    extra = 0
    readonly_fields = ('team_id',)


@admin.register(models.Community)
class CommunityAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for Community model.
    """
    list_display = ("custom_name", "is_available",)
    list_filter = ("is_available",)
    readonly_fields = ("collections",)
    inlines = [TeamInline]
    form = CommunityForm


@admin.register(models.SurfTeam)
class SurfTeamAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for SURFconext Team model.
    """

    list_display = ("external_id", "name", "description",)
