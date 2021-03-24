from django.db import models
from django.utils.timezone import datetime, make_aware

from core.constants import HarvestStages, HARVEST_STAGE_CHOICES
from core.models.datatypes.dataset import Dataset


class OAIPMHRepositories:
    EDUREP = "edurep.EdurepOAIPMH"
    SHAREKIT = "sharekit.SharekitMetadataHarvest"


OAIPMH_REPOSITORY_CHOICES = [
    (value, attr.lower().capitalize())
    for attr, value in sorted(OAIPMHRepositories.__dict__.items()) if not attr.startswith("_")
]


class OAIPMHSet(models.Model):

    name = models.CharField(max_length=50, help_text="Human readable name")
    datasets = models.ManyToManyField(Dataset, through="OAIPMHHarvest")
    repository = models.CharField(max_length=50, choices=OAIPMH_REPOSITORY_CHOICES)
    spec = models.CharField(
        max_length=255,
        help_text="The setSpec value for an OAI-PMH set"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "OAI-PMH set"
        verbose_name_plural = "OAI-PMH sets"


class OAIPMHHarvest(models.Model):

    source = models.ForeignKey(OAIPMHSet, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)

    latest_update_at = models.DateTimeField(
        null=True, blank=True, default=make_aware(datetime(year=1970, month=1, day=1))
    )
    harvested_at = models.DateTimeField(null=True, blank=True)
    stage = models.CharField(max_length=50, choices=HARVEST_STAGE_CHOICES, default=HarvestStages.NEW)

    def clean(self):
        if not self.id:
            self.stage = HarvestStages.NEW

    def reset(self):
        self.latest_update_at = make_aware(datetime(year=1970, month=1, day=1))
        self.harvested_at = None
        self.stage = HarvestStages.NEW
        self.save()

    class Meta:
        verbose_name = "OAI-PMH harvest"
        verbose_name_plural = "OAI-PMH harvests"
