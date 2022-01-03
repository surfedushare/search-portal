from django.db import models as django_models

from surf.apps.core.models import UUIDModel
from surf.apps.locale.models import LocaleHTML


class Theme(UUIDModel):

    nl_slug = django_models.SlugField(max_length=100, null=True)
    en_slug = django_models.SlugField(max_length=100, null=True)

    created_at = django_models.DateTimeField(auto_now_add=True)
    external_id = django_models.CharField(max_length=255)
    description_translations = django_models.OneToOneField(to=LocaleHTML, on_delete=django_models.CASCADE,
                                                           null=True, blank=False)

    def __str__(self):
        return self.external_id

    class Meta:
        ordering = ("created_at",)
