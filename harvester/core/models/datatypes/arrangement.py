from collections import Iterator
import logging

from django.db import models
from django.contrib.postgres import fields as postgres_fields
from django.utils.functional import cached_property

from datagrowth import settings as datagrowth_settings
from datagrowth.datatypes import CollectionBase, DocumentCollectionMixin
from datagrowth.utils import ibatch


logger = logging.getLogger("harvester")


class Arrangement(DocumentCollectionMixin, CollectionBase):
    """
    When people search in the portal this is what they find.
    The Arrangement is in other words responsible for generating the Elastic Search Document.
    It does this through possibly multiple Datagrowth Documents.
    A Datagrowth Document is akin to a file.
    """

    meta = postgres_fields.JSONField(default=dict)
    deleted_at = models.DateTimeField(null=True, blank=True)
