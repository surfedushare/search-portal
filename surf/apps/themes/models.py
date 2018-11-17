from django.db import models as django_models

from surf.apps.core.models import UUIDModel
from surf.apps.filters.models import FilterCategoryItem


class Theme(UUIDModel):
    description = django_models.TextField(null=True, blank=True)

    external_id = django_models.CharField(
        max_length=255,
        verbose_name="Filter item id in EduRep")

    filter_category_item = django_models.OneToOneField(
        FilterCategoryItem,
        related_name="theme",
        on_delete=django_models.SET_NULL,
        null=True, blank=True)

    disciplines = django_models.ManyToManyField(
        FilterCategoryItem,
        related_name="parent_themes",
        blank=True)

    def __str__(self):
        return self.external_id
