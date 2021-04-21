from datetime import datetime

from django.conf import settings
from django.db.transaction import atomic, DatabaseError
from django.utils.timezone import make_aware
from celery import current_app as app

from datagrowth.configuration import create_config
from datagrowth.resources.http.tasks import send
from datagrowth.utils.iterators import ibatch

from core.constants import Repositories, HarvestStages
from core.models import Harvest, Document
from sharekit.models import SharekitMetadataHarvest


@app.task(name="sync_metadata")
def sync_metadata():
    harvest_queryset = Harvest.objects.filter(
        dataset__harvestsource__repository=Repositories.SHAREKIT,
        stage=HarvestStages.COMPLETE  # prevents syncing materials half way a full harvest
    )
    try:
        with atomic():
            for harvest in harvest_queryset.select_for_update(nowait=True):
                # Recording which time will become latest_update_at
                current_time = make_aware(datetime.now())
                # Getting metadata from Sharekit and stop immediately if anything went wrong
                send_config = create_config("http_resource", {
                    "resource": harvest.source.repository,
                    "continuation_limit": 1000,
                })
                set_specification = harvest.source.spec
                scc, err = send(
                    set_specification, f"{harvest.latest_update_at:%Y-%m-%d}",
                    config=send_config,
                    method="get"
                )
                if len(err):
                    continue
                # Now parse the metadata and update Documents
                seeds = SharekitMetadataHarvest.objects.extract_seeds(set_specification, harvest.latest_update_at)
                for seeds_batch in ibatch(seeds, batch_size=32):
                    documents_queryset = Document.objects.filter(
                        reference__in=[seed["external_id"] for seed in seeds_batch]
                    )
                    documents = {
                        doc.properties["external_id"]: doc
                        for doc in documents_queryset
                    }
                    for seed in seeds_batch:
                        language = seed.pop("language")
                        title = seed["title"]
                        mime_type = seed["mime_type"]
                        document = documents[seed["external_id"]]
                        document.properties.update(seed)
                        document.properties["language"]["metadata"] = language
                        document.properties["suggest"] = title
                        document.properties["file_type"] = settings.MIME_TYPE_TO_FILE_TYPE[mime_type]
                    Document.objects.bulk_update(documents.values(), ["properties"])
                # Last but not least we update the harvest update time to get a different delta later
                harvest.latest_update_at = current_time
                harvest.save()
    except DatabaseError:  # select_for_update lock failed
        pass
