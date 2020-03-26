"""
This module provides django admin functionality for communities app.
"""
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from surf.apps.communities import models
from surf.apps.communities.models import PublishStatus, REQUIRED_LANGUAGES


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

    class Meta:
        model = models.Community
        fields = '__all__'
        exclude = ['members']


class TeamInline(admin.TabularInline):
    model = models.Team
    extra = 0
    readonly_fields = ('team_id',)


class CommunityDetailInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        languages = REQUIRED_LANGUAGES
        print("CLEANING HERE")
        for form in self.forms:
            print(f"FORMN {form}")
            print(f"CLEANING THIS FORM {form.cleaned_data}")
            try:
                language_code = form.cleaned_data['language_code'].upper()
                if language_code in languages:
                    languages.remove(language_code)
            except KeyError as exc:
                continue
        if len(languages) != 0:
            raise ValidationError(f"Required language code(s) {str(languages)} not in community details.")


class CommunityDetailInline(admin.StackedInline):
    model = models.CommunityDetail
    formset = CommunityDetailInlineFormset
    extra = 0


@admin.register(models.Community)
class CommunityAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for Community model.
    """
    list_display = ("name", "publish_status",)
    list_filter = ("publish_status", TrashListFilter,)
    readonly_fields = ("deleted_at",)
    inlines = [TeamInline, CommunityDetailInline]
    form = CommunityForm

    actions = [restore_nodes, trash_nodes]

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj is not None:
            fields += ("external_id",)
        return fields

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
