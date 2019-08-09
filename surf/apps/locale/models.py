from django.db import models

from surf.apps.core.models import UUIDModel

class Locale(UUIDModel):

    asset = models.CharField('Asset ID', max_length=512, unique=True)
    en = models.CharField('English, en', max_length=5120, null=True, blank=True)
    nl = models.CharField('Dutch, nl', max_length=5120, null=False, blank=False)
    is_fuzzy = models.BooleanField(default=False)

    def __str__(self):
        return self.asset

    def toJSON(self):
        return {
            "en": self.en,
            "nl": self.nl
        }

    class Meta:
        verbose_name = "Localization"
        verbose_name_plural = "Localizations"


from django.db import models

from surf.apps.core.models import UUIDModel


class LocaleHTML(UUIDModel):

    asset = models.CharField('Asset ID', max_length=512, unique=True)
    en = models.TextField('English, en', max_length=16384, null=True, blank=True)
    nl = models.TextField('Dutch, nl', max_length=16384, null=False, blank=False)
    is_fuzzy = models.BooleanField(default=False)

    def __str__(self):
        return self.asset

    class Meta:
        verbose_name = "Localization with HTML"
        verbose_name_plural = "Localizations with HTML"
