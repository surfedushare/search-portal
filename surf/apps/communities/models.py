"""
This module contains implementation of models for communities app.
"""

from django.db import models as django_models
from django.conf import settings

from surf.apps.core.models import UUIDModel

from surf.apps.materials.models import Collection
from surf.apps.locale.models import Locale, LocaleHTML


class SurfTeam(UUIDModel):
    """
    Implementation of SURFconext Team model.
    """

    # identifier of SURFconext Team
    external_id = django_models.CharField(max_length=255,
                                          verbose_name="SURFconext group id")

    name = django_models.CharField(max_length=255)
    description = django_models.TextField(blank=True)

    # list of community administrators
    admins = django_models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Administrators",
        related_name='admin_teams',
        blank=True)

    # list of community members
    members = django_models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Members",
        related_name='teams',
        blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Community(UUIDModel):
    """
    Implementation of Community model. Communities are related to
    SURFconext Teams.
    """

    surf_team = django_models.OneToOneField(SurfTeam,
                                            on_delete=django_models.CASCADE,
                                            related_name="community",
                                            null=True)

    name = django_models.CharField(max_length=255, blank=True)
    description = django_models.TextField(blank=True)

    logo = django_models.ImageField(
        upload_to='communities',
        blank=True,
        null=True,
        help_text="The proportion of the image should be 230x136")

    featured_image = django_models.ImageField(
        upload_to='communities',
        blank=True,
        null=True,
        help_text="The proportion of the image should be 388x227")

    website_url = django_models.URLField(blank=True, null=True)

    # is this community available for users
    is_available = django_models.BooleanField(
        verbose_name="Is community available in service",
        default=True)

    # list of community collections
    collections = django_models.ManyToManyField(Collection,
                                                blank=True,
                                                related_name="communities")

    # identifier of SURFconext Team
    external_id = django_models.CharField(max_length=255,
                                          verbose_name="SurfConext group id",
                                          null=True, blank=True)

    # list of community administrators
    admins = django_models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Administrators",
        related_name='admin_communities',
        blank=True)

    # list of community members
    members = django_models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Members",
        related_name='communities',
        blank=True)

    title_translations = django_models.OneToOneField(to=Locale, on_delete=django_models.CASCADE,
                                                     null=True, blank=False)
    description_translations = django_models.OneToOneField(to=LocaleHTML, on_delete=django_models.CASCADE,
                                                           null=True, blank=False)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Communities'

    def __str__(self):
        return self.name
