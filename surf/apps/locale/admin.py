import json

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.conf.urls import url
from django.contrib.staticfiles.storage import staticfiles_storage as default_storage
from django.core.files.base import ContentFile
from django import forms

from ckeditor.widgets import CKEditorWidget

from surf.apps.locale.models import Locale, LocaleHTML


@admin.register(Locale)
class LocaleAdmin(admin.ModelAdmin):
    list_display = ('asset', 'en', 'nl',)
    search_fields = ('asset', 'en', 'nl',)
    list_editable = ('en', 'nl',)

    def get_model_info(self):
        app_label = self.model._meta.app_label
        return app_label, self.model._meta.model_name

    def get_urls(self):
        urls = super().get_urls()
        info = self.get_model_info()
        custom_urls = [
            url(
                r'^export_i18n_json/$',
                self.admin_site.admin_view(self.process_update_i18n_json),
                name='{}_{}_updatejson'.format(*info),
            ),
        ]
        rv = custom_urls + urls
        return rv

    def process_update_i18n_json(self, request, *args, **kwargs):
        localizations = list(Locale.objects.values('asset', 'en', 'nl'))

        loc_en = {}
        loc_nl = {}

        for l in localizations:
            loc_en[l['asset']] = l['en']
            loc_nl[l['asset']] = l['nl']

        en_str = json.dumps(loc_en)
        nl_str = json.dumps(loc_nl)

        default_storage.delete('locales/en/surf-en.json')
        default_storage.save('locales/en/surf-en.json', ContentFile(en_str))

        default_storage.delete('locales/nl-NL/surf-nl-NL.json')

        default_storage.save(
            'locales/nl-NL/surf-nl-NL.json', ContentFile(nl_str))

        self.message_user(request, 'Localization successfully updated')

        return HttpResponseRedirect(
            reverse_lazy('admin:locale_locale_changelist'))


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
