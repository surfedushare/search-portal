from django.db import models

from surf.apps.core.models import UUIDModel


class Locale(UUIDModel):
    asset = models.CharField('Asset ID', max_length=512, unique=True)

    en = models.CharField('English, en', max_length=5120,
                          null=True, blank=True)

    nl = models.CharField('Dutch, nl-NL',
                          max_length=5120, null=True, blank=True)

    def __str__(self):
        return self.asset

    class Meta:
        verbose_name = "textstring"
        verbose_name_plural = "Localization"
