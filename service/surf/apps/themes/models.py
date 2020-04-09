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

    description = django_models.TextField(null=True, blank=True)

    external_id = django_models.CharField(max_length=255)

    # related Filter Category item
    filter_category_item = django_models.OneToOneField(
        MpttFilterItem,
        related_name="theme",
        on_delete=django_models.SET_NULL,
        null=True, blank=True)

    # the list of related disciplines
    disciplines = django_models.ManyToManyField(
        MpttFilterItem,
        related_name="parent_themes",
        blank=True)

    title_translations = django_models.OneToOneField(to=Locale, on_delete=django_models.CASCADE,
                                                     null=True, blank=False)
    description_translations = django_models.OneToOneField(to=LocaleHTML, on_delete=django_models.CASCADE,
                                                           null=True, blank=False)

    def __str__(self):
        return self.external_id
