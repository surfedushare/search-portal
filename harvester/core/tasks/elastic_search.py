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
                        elif language and language not in settings.ELASTICSEARCH_ANALYSERS and index.language == "unk":
                            docs.append(doc.to_search())
                    errors = index.push(chain(*docs), recreate=False)
                    for error in errors:
                        logger.error(f"Unable to index {error['index']['_id']}: {error['index']['error']}")
                extensions_queryset = Extension.objects.filter(
                    modified_at__gte=index.pushed_at,
                    is_addition=True
                )
                for ext_batch in ibatch(extensions_queryset, batch_size=32):
                    exts = [ext.to_search() for ext in ext_batch if ext.get_language() == index.language]
                    index.push(chain(*exts), recreate=False)
                    for error in errors:
                        logger.error(f"Unable to index {error['index']['_id']}: {error['index']['error']}")
                index.pushed_at = current_time
                index.save()
    except DatabaseError:
        logger.warning("Unable to acquire a database lock for sync_indices")
