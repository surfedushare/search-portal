from django.db import models as django_models
from django.conf import settings

from surf.apps.core.models import UUIDModel


class Community(UUIDModel):
    external_id = django_models.CharField(max_length=255,
                                          verbose_name="SurfConext group id")

    name = django_models.CharField(max_length=255)
    description = django_models.TextField(blank=True)

    logo = django_models.ImageField(upload_to='communities',
                                    blank=True,
                                    null=True,)

    featured_image = django_models.ImageField(upload_to='communities',
                                              blank=True,
                                              null=True,)

    website_url = django_models.URLField(blank=True, null=True)

    admins = django_models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Administrators",
        related_name='admin_communities',
        blank=True)

    members = django_models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Members",
        related_name='communities',
        blank=True)

    is_available = django_models.BooleanField(
        verbose_name="Is community available in service",
        default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Communities'

    def __str__(self):
        return self.name
