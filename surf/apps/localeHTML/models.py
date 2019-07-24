from django.db import models

from surf.apps.core.models import UUIDModel


class LocaleHTML(UUIDModel):
    asset = models.CharField('Asset ID', max_length=512, unique=True)

    en = models.TextField('English, en', max_length=16384, null=True, blank=True)

    nl = models.TextField('Dutch, nl-NL', max_length=16384, null=True, blank=True)

    def __str__(self):
        return self.asset

    class Meta:
        verbose_name = "Localization with HTML"
        verbose_name_plural = "Localizations with HTML"
