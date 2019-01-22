"""
This module contains implementation of models for filters app.
"""

from django.db import models as django_models
from django.conf import settings
from django.core import validators

from surf.apps.core.models import UUIDModel


class FilterCategory(UUIDModel):
    """
    Implementation of Filter Category model. Filter Categories should be
    configured in Django admin page.
    """

    title = django_models.CharField(max_length=255)

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
