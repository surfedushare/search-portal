"""
This module contains implementation of models for filters app.
"""

from django.db import models as django_models
from django.conf import settings
from django.core import validators

from surf.apps.core.models import UUIDModel
from surf.apps.locale.models import Locale

from mptt.models import MPTTModel, TreeForeignKey
import json


class FilterCategory(UUIDModel):
    """
    Implementation of Filter Category model. Filter Categories should be
    configured in Django admin page.
    """
    title = django_models.CharField(max_length=255)
    title_translations = django_models.OneToOneField(to=Locale, on_delete=django_models.CASCADE,
                                                     null=True, blank=False)

    # LOM identifier of field category in EduRep
    edurep_field_id = django_models.CharField(
        max_length=255,
        verbose_name="Field id in EduRep")

    # max number of category items that should be loaded from EduRep.
    # 0 - should be loaded all items of category
    max_item_count = django_models.IntegerField(
        default=0,
        validators=[validators.MinValueValidator(0)])

    def __str__(self):
        return self.title


class FilterCategoryItem(UUIDModel):
    """
    Implementation of Filter Category item model. Filter Category items are
    loaded from EduRep via EduRep API.
    """

    title = django_models.CharField(max_length=255)

    # identifier of field category item in EduRep
    external_id = django_models.CharField(
        max_length=255,
        verbose_name="Filter item id in EduRep")

    # related filter category
    category = django_models.ForeignKey(FilterCategory,
                                        verbose_name="Filter category",
                                        related_name='items',
                                        on_delete=django_models.CASCADE)

    order = django_models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Filter(UUIDModel):
    """
    Implementation of user custom Filter model.
    """

    title = django_models.CharField(max_length=255)

    # the user who created the filter
    owner = django_models.ForeignKey(settings.AUTH_USER_MODEL,
                                     verbose_name="Owner",
                                     related_name='filters',
                                     on_delete=django_models.CASCADE)

    # start date to filter materials by their publish date
    start_date = django_models.DateField(blank=True, null=True)

    # end date to filter materials by their publish date
    end_date = django_models.DateField(blank=True, null=True)

    # the number of materials found according to filter
    materials_count = django_models.IntegerField(default=0)

    def __str__(self):
        return self.title


class FilterItem(UUIDModel):
    """
    Implementation of user custom Filter item model.
    """

    # related filter
    filter = django_models.ForeignKey(Filter,
                                      related_name='items',
                                      on_delete=django_models.CASCADE)

    # Filter category item related to this item
    category_item = django_models.ForeignKey(FilterCategoryItem,
                                             related_name='filter_items',
                                             on_delete=django_models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.filter.title, self.category_item.title)


class MpttFilterItem(MPTTModel):
    name = django_models.CharField(max_length=255, unique=True)
    parent = TreeForeignKey('self', on_delete=django_models.CASCADE, null=True, blank=True, related_name='children')

    created_at = django_models.DateTimeField(auto_now_add=True)
    updated_at = django_models.DateTimeField(auto_now=True)
    deleted_from_edurep_at = django_models.DateTimeField(default=None, null=True, blank=True)

    title_translations = django_models.OneToOneField(to=Locale, on_delete=django_models.CASCADE, null=True, blank=False)
    external_id = django_models.CharField(max_length=255, verbose_name="Field id in EduRep", blank=True)
    enabled_by_default = django_models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def to_dict(self):
        #'Yes' if fruit == 'Apple' else 'No'

        return {
            "name": self.name,
            #"parent": str(self.parent),
            "created_at": self.created_at.strftime('%c'),
            "updated_at": self.updated_at.strftime('%c'),
            "title_translations": self.title_translations.toJSON() if self.title_translations else None,
            "external_id": self.external_id,
            "enabled_by_default": self.enabled_by_default
        }

    def toJSON(self):
        return json.dumps(self.to_dict())

    class MPTTMeta:
        order_insertion_by = ['name']
