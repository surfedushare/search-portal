
from django.utils import timezone
from django.db import models


class QueryLog(models.Model):
    timestamp = models.DateTimeField(editable=False, default=timezone.now)
    search_text = models.TextField()
    filters = models.TextField()

    query_url = models.TextField()
    result_size = models.IntegerField()
    result = models.TextField()
