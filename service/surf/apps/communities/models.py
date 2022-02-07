"""
This module contains implementation of models for communities app.
"""
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, URLValidator, validate_image_file_extension
from django.db import models as django_models
from django.utils import timezone
from django_enumfield import enum

from surf.apps.core.models import UUIDModel

from surf.apps.materials.models import Collection
from surf.statusenums import PublishStatus

REQUIRED_LANGUAGES = ['NL', 'EN']


class Community(UUIDModel):
    """
    Implementation of Community model. Communities are related to
    SURFconext Teams.
    """
    publish_status = enum.EnumField(PublishStatus, default=PublishStatus.DRAFT)

    name = django_models.CharField(max_length=255, blank=False)
    deleted_at = django_models.DateTimeField(null=True, blank=True)

    members = django_models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Team',
        blank=True,
    )

    # list of community collections
    collections = django_models.ManyToManyField(Collection, blank=True, related_name="communities")
    # identifier of SURFconext Team
    external_id = django_models.CharField(max_length=255, verbose_name="SurfConext group id", null=True, blank=True)

    publisher = django_models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Publisher name that published most materials in this community. Powers community search."
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Communities'

    def restore(self):
        self.deleted_at = None
        self.save()

    def delete(self, using=None, keep_parents=False):
        if not self.deleted_at:
            self.deleted_at = timezone.now()
            self.save()
        else:
            super().delete(using=using, keep_parents=keep_parents)

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


def validate_logo_size(image):
    return


def validate_featured_size(image):
    return


class CommunityDetail(django_models.Model):
    community = django_models.ForeignKey(Community, on_delete=django_models.CASCADE, related_name='community_details')
    language_code = django_models.CharField(max_length=2)
    title = django_models.CharField(max_length=255, validators=[MinLengthValidator(1)])
    description = django_models.TextField(max_length=16384, null=True, blank=True)
    website_url = django_models.URLField(blank=True, null=True, validators=[URLValidator])

    logo = django_models.ImageField(upload_to='communities', blank=True, null=True,
                                    validators=[validate_image_file_extension])

    featured_image = django_models.ImageField(upload_to='communities', blank=True, null=True,
                                              validators=[validate_image_file_extension])

    class Meta:
        # only allow unique language codes for communities
        constraints = [
            django_models.UniqueConstraint(fields=['language_code', 'community'], name='unique languages in community')
        ]

    def clean(self):
        # force consistency
        self.language_code = self.language_code.upper()

    def __str__(self):
        return self.title


class Team(django_models.Model):
    community = django_models.ForeignKey(Community, on_delete=django_models.CASCADE)
    user = django_models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=django_models.CASCADE)
    team_id = django_models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Member'

    def clean(self):
        if not self.community.external_id:
            raise ValidationError("Community SURFconext group id isn't set, can't add users to this community.")
        self.team_id = self.community.external_id
