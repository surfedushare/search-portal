from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType


class Batch(models.Model):

    processor = models.CharField(max_length=256)
    documents = models.ManyToManyField(to="Document", through="ProcessResult")

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class ProcessResult(models.Model):

    document = models.ForeignKey("Document", on_delete=models.CASCADE)
    batch = models.ForeignKey("Batch", on_delete=models.CASCADE)

    result = GenericForeignKey(ct_field="result_type", fk_field="result_id")
    result_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE)
    result_id = models.PositiveIntegerField(null=True, blank=True)
