"""
This module contains implementation of core models.
"""

import uuid

from django.db import models


class UUIDModel(models.Model):
    """
    Implementation of base model with UUID identifier.
    """

    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)

    class Meta:
        abstract = True
