from django.db import models as django_models
from django.conf import settings
from django.core import validators

from surf.apps.core.models import UUIDModel


class FilterCategory(UUIDModel):
    title = django_models.CharField(max_length=255)

    edurep_field_id = django_models.CharField(
        max_length=255,
        verbose_name="Field id in EduRep")

    max_item_count = django_models.IntegerField(
        default=0,
        validators=[validators.MinValueValidator(0)])

    def __str__(self):
        return self.title


class FilterCategoryItem(UUIDModel):
    title = django_models.CharField(max_length=255)

    external_id = django_models.CharField(
        max_length=255,
        verbose_name="Filter item id in EduRep")

    category = django_models.ForeignKey(FilterCategory,
                                        verbose_name="Filter category",
                                        related_name='items',
                                        on_delete=django_models.CASCADE)

    def __str__(self):
        return self.title


class Filter(UUIDModel):
    title = django_models.CharField(max_length=255)

    owner = django_models.ForeignKey(settings.AUTH_USER_MODEL,
                                     verbose_name="Owner",
                                     related_name='filters',
                                     on_delete=django_models.CASCADE)

    def __str__(self):
        return self.title


class FilterItem(UUIDModel):
    filter = django_models.ForeignKey(Filter,
                                      related_name='items',
                                      on_delete=django_models.CASCADE)

    category_item = django_models.ForeignKey(FilterCategoryItem,
                                             related_name='filter_items',
                                             on_delete=django_models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.filter.title, self.category_item.title)
