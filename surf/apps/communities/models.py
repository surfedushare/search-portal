"""
This module contains implementation of models for communities app.
"""

from django.db import models as django_models
from django.conf import settings

from surf.apps.core.models import UUIDModel

from surf.apps.materials.models import Collection


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

    # identifier of SURFconext Team
    # should be removed
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

    # list of community administrators
    # should be removed
    admins = django_models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Administrators",
        related_name='admin_communities',
        blank=True)

    # list of community members
    # should be removed
    members = django_models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Members",
        related_name='communities',
        blank=True)

    # is this community available for users
    is_available = django_models.BooleanField(
        verbose_name="Is community available in service",
        default=True)

    # list of community collections
    collections = django_models.ManyToManyField(Collection,
                                                blank=True,
                                                related_name="communities")

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Communities'

    def __str__(self):
        return self.name
