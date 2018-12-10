"""
This module provides django admin functionality for communities app.
"""

from django.contrib import admin
from django import forms
from django.db.models import Q

from surf.apps.communities import models


class CommunityForm(forms.ModelForm):
    """
    Implementation of Community Form class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            # choose only SurfTeam instances not related to Community instances
            qs = models.SurfTeam.objects
            conditions = Q(community__isnull=True)
            if self.instance and self.instance.pk:
                conditions |= Q(community__id=self.instance.pk)
            qs = qs.filter(conditions)
            self.fields['surf_team'].queryset = qs.all()
        except AttributeError:
            pass

    class Meta:
        model = models.Community
        exclude = ("external_id", "admins", "members",)


@admin.register(models.Community)
class CommunityAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for Community model.
    """

    list_display = ("custom_name", "custom_description", "is_available",)
    list_filter = ("is_available",)
    exclude = ("external_id", "admins", "members",)
    form = CommunityForm

    def custom_name(self, obj):
        if obj.name:
            return obj.name
        else:
            return obj.surf_team.name

    def custom_description(self, obj):
        if obj.description:
            return obj.description
        else:
            return obj.surf_team.description

    custom_description.short_description = 'Description'


@admin.register(models.SurfTeam)
class SurfTeamAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for SURFconext Team model.
    """

    list_display = ("external_id", "name", "description",)
