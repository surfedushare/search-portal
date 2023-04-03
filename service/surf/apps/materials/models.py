"""
This module contains implementation of models for materials app.
"""

from django.db import models as django_models
from django.db.models import F
from django.utils import timezone
from django_enumfield import enum

from surf.apps.core.search import get_search_client
from surf.apps.core.models import UUIDModel
from surf.statusenums import PublishStatus


RESOURCE_TYPE_MATERIAL = "material"
RESOURCE_TYPE_COLLECTION = "collection"


class Material(UUIDModel):
    """
    Implementation of EduRep Material model.
    """

    # identifier of material in EduRep
    external_id = django_models.CharField(max_length=255,
                                          verbose_name="EduRep material id")

    deleted_at = django_models.DateTimeField(null=True, blank=True, default=None)

    star_1 = django_models.PositiveIntegerField(default=0)
    star_2 = django_models.PositiveIntegerField(default=0)
    star_3 = django_models.PositiveIntegerField(default=0)
    star_4 = django_models.PositiveIntegerField(default=0)
    star_5 = django_models.PositiveIntegerField(default=0)
    # a user can applaud a material many times more than he can star rate it
    applaud_count = django_models.BigIntegerField(default=0)
    view_count = django_models.BigIntegerField(default=0)

    def get_star_count(self):
        return self.star_1 + self.star_2 + self.star_3 + self.star_4 + self.star_5
    get_star_count.short_description = 'Star rating count'

    def get_avg_star_rating(self):
        total_stars = 1 * self.star_1 + 2 * self.star_2 + 3 * self.star_3 + 4 * self.star_4 + 5 * self.star_5
        star_count = self.get_star_count()
        if star_count > 0:
            return round(total_stars / star_count, 1)
        return 0
    get_avg_star_rating.short_description = 'Average star rating'

    def restore(self):
        self.deleted_at = None
        self.save()

    def delete(self, using=None, keep_parents=False):
        if not self.deleted_at:
            self.deleted_at = timezone.now()
            self.save()
        else:
            super().delete(using=using, keep_parents=keep_parents)

    def sync_info(self):
        assert self.external_id, "Can't sync info if instance doesn't have an external id"

        # Fetch data from search engine
        client = get_search_client()
        response = client.get_materials_by_id([self.external_id])
        records = response.get("records", [])
        if not records:
            if not self.deleted_at:
                self.delete()
            return

        # Update the model
        if self.deleted_at:  # we restore materials if they reappear in an index
            self.deleted_at = None
        self.save()

    def __str__(self):
        return self.external_id


class Collection(UUIDModel):
    """
    Implementation of Collection model.
    """

    title_nl = django_models.CharField(max_length=255, blank=True, null=True)
    title_en = django_models.CharField(max_length=255, blank=True, null=True)

    # the list of collection materials
    materials = django_models.ManyToManyField(Material,
                                              blank=True,
                                              related_name="collections",
                                              through='CollectionMaterial')

    is_shared = django_models.BooleanField(default=False)
    publish_status = enum.EnumField(PublishStatus, default=PublishStatus.DRAFT)
    created_at = django_models.DateTimeField(auto_now_add=True)
    deleted_at = django_models.DateTimeField(null=True)
    position = django_models.IntegerField(default=0)

    def restore(self):
        self.deleted_at = None
        self.save()

    def delete(self, using=None, keep_parents=False):
        if not self.deleted_at:
            self.deleted_at = timezone.now()
            self.save()

        super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return self.title_nl

    class Meta:
        ordering = ("created_at",)


class CollectionMaterial(django_models.Model):
    collection = django_models.ForeignKey(Collection, on_delete=django_models.CASCADE)
    material = django_models.ForeignKey(Material, on_delete=django_models.CASCADE)
    featured = django_models.BooleanField(default=False)
    position = django_models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Material'
        constraints = [
            django_models.UniqueConstraint(fields=['collection', 'material'], name='unique materials in collection')
        ]


class SharedResourceCounter(UUIDModel):
    """
    Implementation of model for counter of shared resource.
    This model is used to store counter values for different shared objects.
    """

    counter_key = django_models.CharField(max_length=255, unique=True)
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

        c.counter_value = F('counter_value') + 1
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
