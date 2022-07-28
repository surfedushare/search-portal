from datetime import datetime
from itertools import chain

from django.conf import settings
from django.db.transaction import atomic, DatabaseError
from django.utils.timezone import make_aware
from celery import current_app as app

from datagrowth.utils.iterators import ibatch

from harvester.tasks.base import DatabaseConnectionResetTask
from core.logging import HarvestLogger
from core.models import ElasticIndex, DatasetVersion, Extension


@app.task(name="sync_indices", base=DatabaseConnectionResetTask)
def sync_indices():
    dataset_version = DatasetVersion.objects.get_current_version()
    if dataset_version is None:
        return
    logger = HarvestLogger(dataset_version.dataset.name, "sync_indices", {})
    indices_queryset = ElasticIndex.objects.filter(dataset_version=dataset_version, pushed_at__isnull=False)
    try:
        with atomic():
            current_time = make_aware(datetime.now())
            for index in indices_queryset.select_for_update(nowait=True):
                documents_queryset = dataset_version.document_set.filter(
                    modified_at__gte=index.pushed_at
                )
                for doc_batch in ibatch(documents_queryset, batch_size=32):
                    docs = []
                    for doc in doc_batch:
                        language = doc.get_language()
                        if language == index.language:
                            docs.append(doc.to_search())
                        elif language and language not in settings.OPENSEARCH_ANALYSERS and index.language == "unk":
                            docs.append(doc.to_search())
                    errors = index.push(chain(*docs), recreate=False)
                    logger.open_search_errors(errors)
                extensions_queryset = Extension.objects.filter(
                    modified_at__gte=index.pushed_at,
                    is_addition=True
                )
                for ext_batch in ibatch(extensions_queryset, batch_size=32):
                    exts = [ext.to_search() for ext in ext_batch if ext.get_language() == index.language]
                    errors = index.push(chain(*exts), recreate=False)
                    logger.open_search_errors(errors)
                index.pushed_at = current_time
                index.save()
    except DatabaseError:
        logger.warning("Unable to acquire a database lock for sync_indices")
