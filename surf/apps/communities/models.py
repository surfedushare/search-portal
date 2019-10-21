"""
This module contains implementation of models for communities app.
"""

from django.db import models as django_models
from django.conf import settings

from surf.apps.core.models import UUIDModel

from surf.apps.materials.models import Collection
from surf.apps.locale.models import Locale, LocaleHTML

from django_enumfield import enum


class PublishStatus(enum.Enum):
    DRAFT = 0
    REVIEW = 1
    PUBLISHED = 2

    __labels__ = {
        DRAFT: "Draft",
        REVIEW: "Review",
        PUBLISHED: "Published",
    }


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
    publish_status = enum.EnumField(PublishStatus, default=PublishStatus.DRAFT)
    name = django_models.CharField(max_length=255, blank=True)
    description = django_models.TextField(blank=True)
    title_translations = django_models.OneToOneField(to=Locale, on_delete=django_models.CASCADE,
                                                     null=True, blank=False)
    description_translations = django_models.OneToOneField(to=LocaleHTML, on_delete=django_models.CASCADE,
                                                           null=True, blank=False)

    # list of community members
    members = django_models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Members",
        related_name='communities',
        blank=True)

    new_members = django_models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Team',
        blank=True,
    )

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

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Communities'

    def __str__(self):
        return self.name

    def clean(self):
        # Check whether the entered external_id is a valid URN.
        # regex taken from the O'Reilly Regular Expressions Cookbook, 2nd Edition
        # https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch08s06.html
        if self.external_id:
            regex = r"^urn:[a-z0-9][a-z0-9-]{0,31}:[a-z0-9()+,\-.:=@;$_!*'%/?#]+$"
            if not re.match(regex, self.external_id):
                raise ValidationError("SURFconext group id isn't a valid URN. Check "
                                      "https://en.wikipedia.org/wiki/Uniform_Resource_Name for examples of valid URNs.")


class Team(django_models.Model):
    community = django_models.ForeignKey(Community, on_delete=django_models.CASCADE)
    user = django_models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=django_models.CASCADE)
    team_id = django_models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Member'

    def clean(self):
        self.team_id = self.community.external_id
