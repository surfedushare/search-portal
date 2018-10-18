from django.db import models as django_models
from django.conf import settings

from surf.apps.core.models import UUIDModel


class Material(UUIDModel):
    external_id = django_models.CharField(max_length=255,
                                          verbose_name="EduRep material id")

    def __str__(self):
        return self.external_id


class Collection(UUIDModel):
    title = django_models.CharField(max_length=255)

    owner = django_models.ForeignKey(settings.AUTH_USER_MODEL,
                                     verbose_name="Owner",
                                     related_name='collections',
                                     on_delete=django_models.CASCADE)

    materials = django_models.ManyToManyField(Material,
                                              related_name="collections")

    def __str__(self):
        return self.title
