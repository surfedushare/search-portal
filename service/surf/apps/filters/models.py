"""
This module contains implementation of models for filters app.
"""

from django.conf import settings
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
    enabled_by_default = django_models.BooleanField(default=False)
    is_hidden = django_models.BooleanField(default=False)

    item_count = 0

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = "filter category item"


class Filter(object):
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


class FilterItem(object):
    """
    Implementation of user custom Filter item model.
    """

    # related filter
    filter = django_models.ForeignKey("Filter",
                                      related_name='items',
                                      on_delete=django_models.CASCADE)

    # Filter category item related to this item
    mptt_category_item = django_models.ForeignKey(MpttFilterItem,
                                                  related_name='filter_items',
                                                  on_delete=django_models.CASCADE,
                                                  null=True)

    def __str__(self):
        return "{} - {}".format(self.filter.title, self.mptt_category_item.name)
