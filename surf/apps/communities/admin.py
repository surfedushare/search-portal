"""
This module provides django admin functionality for communities app.
"""

from django.contrib import admin
from django import forms
from django.core.files.images import get_image_dimensions

from surf.apps.communities import models
from surf.apps.communities.models import PublishStatus


def trash_nodes(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()


trash_nodes.short_description = "Trash selected %(verbose_name_plural)s"


def restore_nodes(modeladmin, request, queryset):
    for obj in queryset:
        obj.restore()


restore_nodes.short_description = "Restore selected %(verbose_name_plural)s"


class TrashListFilter(admin.SimpleListFilter):

    title = 'is trash'
    parameter_name = 'trash'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Yes'),
            ('0', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value() or '0'
        try:
            is_trash = bool(int(value))
        except ValueError:
            is_trash = False
        return queryset.filter(deleted_at__isnull=not is_trash)


class CommunityForm(forms.ModelForm):
    """
    Implementation of Community Form class.
    """
    publish_status = forms.TypedChoiceField(choices=PublishStatus.choices(), coerce=int)

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
    list_display = ("name", "publish_status",)
    list_filter = ("publish_status", TrashListFilter,)
    readonly_fields = ("deleted_at",)
    inlines = [TeamInline]
    form = CommunityForm

    actions = [restore_nodes, trash_nodes]

    def get_actions(self, request):
        actions = super().get_actions(request)
        try:
            filter_trash = bool(int(request.GET.get('trash', '0')))
        except ValueError:
            filter_trash = False
        if filter_trash:
            del actions["trash_nodes"]
        else:
            del actions["delete_selected"]
            del actions["restore_nodes"]
        return actions


@admin.register(models.SurfTeam)
class SurfTeamAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for SURFconext Team model.
    """

    list_display = ("external_id", "name", "description",)
