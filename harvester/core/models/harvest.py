from django.db import models
from django.apps import apps
from django.utils.timezone import datetime, make_aware, timedelta
from django.contrib.postgres.fields import JSONField

from core.constants import (HarvestStages, HARVEST_STAGE_CHOICES, REPOSITORY_CHOICES, DeletePolicies,
                            DELETE_POLICY_CHOICES)
from core.models.datatypes.dataset import Dataset


def thirty_days_default():
    return {"days": 30}


class HarvestSource(models.Model):

    name = models.CharField(max_length=50, help_text="Human readable name")
    datasets = models.ManyToManyField(Dataset, through="Harvest")
    repository = models.CharField(max_length=50, choices=REPOSITORY_CHOICES)
    spec = models.CharField(
        max_length=255,
        help_text="The code for the 'set' you want to harvest"
    )
    delete_policy = models.CharField(max_length=50, choices=DELETE_POLICY_CHOICES, default=DeletePolicies.TRANSIENT)
    purge_interval = JSONField(default=thirty_days_default)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def clear_repository_resources(self):
        harvest_resource = apps.get_model(self.repository)
        harvest_resource.objects.filter(set_specification=self.spec).delete()

    def __str__(self):
        return self.name


class Harvest(models.Model):

    source = models.ForeignKey(HarvestSource, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)

    latest_update_at = models.DateTimeField(
        null=True, blank=True, default=make_aware(datetime(year=1970, month=1, day=1))
    )
    harvested_at = models.DateTimeField(null=True, blank=True)
    purge_after = models.DateTimeField(null=True, blank=True)
    stage = models.CharField(max_length=50, choices=HARVEST_STAGE_CHOICES, default=HarvestStages.NEW)
    is_syncing = models.BooleanField(default=False)

    def clean(self):
        if not self.id:
            self.stage = HarvestStages.NEW
        if not self.purge_after:
            self.purge_after = make_aware(datetime.now()) + timedelta(**self.source.purge_interval)

    def should_purge(self):
        return self.source.delete_policy == DeletePolicies.NO or \
               (self.source.delete_policy == DeletePolicies.TRANSIENT and self.purge_after and
                self.purge_after < make_aware(datetime.now()))

    def prepare(self):
        self.stage = HarvestStages.NEW
        if self.harvested_at:
            self.latest_update_at = self.harvested_at
        self.save()

    def reset(self):
        self.latest_update_at = make_aware(datetime(year=1970, month=1, day=1))
        self.harvested_at = None
        self.stage = HarvestStages.NEW
        self.purge_after = None
        self.clean()
        self.save()
