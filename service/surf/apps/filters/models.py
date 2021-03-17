"""
This module contains implementation of models for filters app.
"""

from django.db import models as django_models
from mptt.models import MPTTModel, TreeForeignKey

from surf.apps.core.models import UUIDModel
from surf.apps.locale.models import Locale


class MpttFilterItem(MPTTModel, UUIDModel):
    name = django_models.CharField(max_length=255)
    parent = TreeForeignKey('self', on_delete=django_models.CASCADE, null=True, blank=True, related_name='children')

    created_at = django_models.DateTimeField(auto_now_add=True)
    updated_at = django_models.DateTimeField(auto_now=True)
    deleted_from_edurep_at = django_models.DateTimeField(default=None, null=True, blank=True)

    title_translations = django_models.OneToOneField(to=Locale, on_delete=django_models.CASCADE, null=True, blank=False)
    external_id = django_models.CharField(max_length=255, verbose_name="Field id in EduRep", blank=False, null=False,
                                          unique=True)
    is_manual = django_models.BooleanField(default=False)
    is_hidden = django_models.BooleanField(default=False)

    item_count = 0

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = "filter category item"
