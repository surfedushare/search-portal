from datetime import datetime

from django.db import models as django_models
from django.conf import settings

from surf.apps.core.models import UUIDModel
from surf.apps.themes.models import Theme
from surf.apps.filters.models import FilterCategoryItem


class Material(UUIDModel):
    external_id = django_models.CharField(max_length=255,
                                          verbose_name="EduRep material id")

    themes = django_models.ManyToManyField(Theme,
                                           blank=True,
                                           related_name="materials")

    disciplines = django_models.ManyToManyField(FilterCategoryItem,
                                                blank=True,
                                                related_name="materials")

    def __str__(self):
        return self.external_id


class Collection(UUIDModel):
    title = django_models.CharField(max_length=255)

    owner = django_models.ForeignKey(settings.AUTH_USER_MODEL,
                                     verbose_name="Owner",
                                     related_name='collections',
                                     on_delete=django_models.CASCADE)

    materials = django_models.ManyToManyField(Material,
                                              blank=True,
                                              related_name="collections")

    is_shared = django_models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ApplaudMaterial(UUIDModel):
    user = django_models.ForeignKey(settings.AUTH_USER_MODEL,
                                    related_name='applauds',
                                    on_delete=django_models.CASCADE)

    material = django_models.ForeignKey(Material,
                                        related_name="applauds",
                                        on_delete=django_models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.user.username, self.material.external_id)


class ViewMaterial(UUIDModel):
    viewed_at = django_models.DateTimeField(default=datetime.now)

    user = django_models.ForeignKey(settings.AUTH_USER_MODEL,
                                    related_name='material_views',
                                    on_delete=django_models.CASCADE)

    material = django_models.ForeignKey(Material,
                                        related_name="material_views",
                                        on_delete=django_models.CASCADE)

    @staticmethod
    def add_unique_view(user, material_external_id):
        if not user or not user.id:
            return

        m, _ = Material.objects.get_or_create(
            external_id=material_external_id,
            defaults=dict(external_id=material_external_id))

        ViewMaterial.objects.update_or_create(
            user_id=user.id, material_id=m.id,
            defaults=dict(viewed_at=datetime.now()))

    def __str__(self):
        return "{} - {}".format(self.user.username, self.material.external_id)
