from django.contrib import admin
from django import forms

from ckeditor.widgets import CKEditorWidget

from surf.vendor.surfconext.models import PrivacyStatement, DataGoal


class DataGoalAdminInline(admin.TabularInline):
    model = DataGoal
    list_display = ("type", "is_active", "priority",)
    extra = 0


class PrivacyStatementForm(forms.ModelForm):

    class Meta:
        model = PrivacyStatement
        widgets = {
            'en': CKEditorWidget(),
            'nl': CKEditorWidget(),
        }
        fields = '__all__'



class PrivacyStatementAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active",)
    form = PrivacyStatementForm
    inlines = (DataGoalAdminInline,)


admin.site.register(PrivacyStatement, PrivacyStatementAdmin)
