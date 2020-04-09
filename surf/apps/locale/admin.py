from django.contrib import admin
from django import forms

from ckeditor.widgets import CKEditorWidget

from surf.apps.locale.models import Locale, LocaleHTML


@admin.register(Locale)
class LocaleAdmin(admin.ModelAdmin):
    list_display = ('asset', 'en', 'nl', 'is_fuzzy',)
    search_fields = ('asset', 'en', 'nl',)
    list_editable = ('en', 'nl', 'is_fuzzy',)
    list_filter = ('is_fuzzy',)


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
    list_display = ('asset', 'en', 'nl', 'is_fuzzy',)
    search_fields = ('asset', 'en', 'nl',)
    list_editable = ('is_fuzzy',)
    list_filter = ('is_fuzzy',)
    form = LocaleHTMLForm
