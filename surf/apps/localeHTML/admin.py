from django.contrib import admin
from django import forms
from surf.apps.localeHTML.models import LocaleHTML

from ckeditor.widgets import CKEditorWidget


class LocaleHTMLForm(forms.ModelForm):
    class Meta:
        model = LocaleHTML
        widgets = {
            'en': CKEditorWidget(),
            'nl': CKEditorWidget(),
        }
        fields = '__all__'


@admin.register(LocaleHTML)
class LocaleHTMLAdmin(admin.ModelAdmin):
    list_display = ('asset', 'en', 'nl',)
    search_fields = ('asset', 'en', 'nl',)
    form = LocaleHTMLForm
