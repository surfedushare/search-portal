from datetime import datetime
from itertools import chain

from django.db.transaction import atomic, DatabaseError
from django.utils.timezone import make_aware
from celery import current_app as app

from datagrowth.utils.iterators import ibatch

from harvester.tasks.base import DatabaseConnectionResetTask
from core.models import ElasticIndex, DatasetVersion


@app.task(name="sync_indices", base=DatabaseConnectionResetTask)
def sync_indices():
    dataset_version = DatasetVersion.objects.get_latest_version()
    indices_queryset = ElasticIndex.objects.filter(dataset_version=dataset_version, pushed_at__isnull=False)
    try:
        with atomic():
            current_time = make_aware(datetime.now())
            for index in indices_queryset.select_for_update(nowait=True):
                documents_queryset = dataset_version.document_set.filter(
                    modified_at__gte=index.pushed_at
                )
                for doc_batch in ibatch(documents_queryset, batch_size=32):
                    docs = [doc.to_search() for doc in doc_batch if doc.get_language() == index.language]
                    index.push(chain(*docs), recreate=False)
                index.pushed_at = current_time
                index.save()
    except DatabaseError:  # select_for_update lock failed
        pass
