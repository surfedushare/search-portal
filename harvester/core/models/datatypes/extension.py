from django.db import models

from datagrowth.datatypes import DocumentBase


class Extension(DocumentBase):

    id = models.CharField(primary_key=True, max_length=100)
    dataset_version = models.ForeignKey("DatasetVersion", blank=True, null=True, on_delete=models.CASCADE)
    # NB: Collection foreign key is added by the base class
    is_parent = models.BooleanField(default=False)
