"""
This module contains implementation of models for themes app.
"""

from django.db import models as django_models

from surf.apps.core.models import UUIDModel
from surf.apps.filters.models import MpttFilterItem
from surf.apps.locale.models import Locale, LocaleHTML


class Theme(UUIDModel):
    """
    Implementation of Theme model. Theme is entity related to the group of
    disciplines.
    """

    created_at = django_models.DateTimeField(auto_now_add=True)
    external_id = django_models.CharField(max_length=255)
    description_translations = django_models.OneToOneField(to=LocaleHTML, on_delete=django_models.CASCADE,
                                                           null=True, blank=False)

    def __str__(self):
        return self.external_id

    class Meta:
        ordering = ("created_at",)
