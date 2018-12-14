"""
This module contains implementation of models for materials app.
"""

from datetime import datetime

from django.db import models as django_models
from django.conf import settings

from surf.apps.core.models import UUIDModel
from surf.apps.themes.models import Theme
from surf.apps.filters.models import FilterCategoryItem


RESOURCE_TYPE_MATERIAL = "material"
RESOURCE_TYPE_COLLECTION = "collection"


class Material(UUIDModel):
    """
    Implementation of EduRep Material model.
    """

    # identifier of material in EduRep
    external_id = django_models.CharField(max_length=255,
                                          verbose_name="EduRep material id")

    # list of related themes
    themes = django_models.ManyToManyField(Theme,
                                           blank=True,
                                           related_name="materials")

    # list of related disciplines
    disciplines = django_models.ManyToManyField(FilterCategoryItem,
                                                blank=True,
                                                related_name="materials")

    material_url = django_models.URLField(blank=True, null=True)
    title = django_models.TextField(blank=True, null=True)
    description = django_models.TextField(blank=True, null=True)
    keywords = django_models.TextField(blank=True, null=True)

    def __str__(self):
        return self.external_id


class Collection(UUIDModel):
    """
    Implementation of Collection model.
    """

    title = django_models.CharField(max_length=255)

    # the user who created the collection
    owner = django_models.ForeignKey(settings.AUTH_USER_MODEL,
                                     verbose_name="Owner",
                                     related_name='collections',
                                     on_delete=django_models.CASCADE)

    # the list of collection materials
    materials = django_models.ManyToManyField(Material,
                                              blank=True,
                                              related_name="collections")

    # does owner share the collection
    is_shared = django_models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ApplaudMaterial(UUIDModel):
    """
    Implementation of Material applaud model. This model is used to collect
    data about material applauds by users.
    """

    user = django_models.ForeignKey(settings.AUTH_USER_MODEL,
                                    related_name='applauds',
                                    on_delete=django_models.CASCADE)

    material = django_models.ForeignKey(Material,
                                        related_name="applauds",
                                        on_delete=django_models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.user.username, self.material.external_id)


class ViewMaterial(UUIDModel):
    """
    Implementation of Material view model. This model is used to collect
    data about material unique view by users.
    """

    viewed_at = django_models.DateTimeField(default=datetime.now)

    user = django_models.ForeignKey(settings.AUTH_USER_MODEL,
                                    related_name='material_views',
                                    on_delete=django_models.CASCADE)

    material = django_models.ForeignKey(Material,
                                        related_name="material_views",
                                        on_delete=django_models.CASCADE)

    @staticmethod
    def add_unique_view(user, material_external_id):
        """
        Updates unique view data
        :param user: user instance
        :param material_external_id: external identifier of material
        """

        if not user or not user.id:
            return

        m, _ = Material.objects.get_or_create(external_id=material_external_id)

        ViewMaterial.objects.update_or_create(
            user_id=user.id, material_id=m.id,
            defaults=dict(viewed_at=datetime.now()))

    def __str__(self):
        return "{} - {}".format(self.user.username, self.material.external_id)


class SharedResourceCounter(UUIDModel):
    """
    Implementation of model for counter of shared resource.
    This model is used to store counter values for different shared objects.
    """

    counter_key = django_models.CharField(max_length=255)
    counter_value = django_models.IntegerField(default=0)
    extra = django_models.CharField(max_length=255, null=True, blank=True)

    @staticmethod
    def increase_counter(counter_key, extra=None):
        """
        Increases the counter value by its key
        :param counter_key: key of counter
        :param extra: extra data for counter
        """

        if not counter_key:
            return

        c, _ = SharedResourceCounter.objects.get_or_create(
            counter_key=counter_key,
            defaults=dict(extra=extra))

        c.counter_value += 1
        c.save()

    @staticmethod
    def create_counter_key(resource_type, resource_id, share_type=None):
        """
        Creates counter key by resource type, id and sharing type
        :param resource_type: the type of resource
        :param resource_id: the identifier of resource
        :param share_type: sharing type of resource (optional)
        :return: created counter key
        """
        if share_type:
            return "{}__{}__{}__".format(resource_type, resource_id,
                                         share_type)
        else:
            return "{}__{}__".format(resource_type, resource_id)

    def __str__(self):
        return "{} - {}".format(self.counter_key, self.extra)
