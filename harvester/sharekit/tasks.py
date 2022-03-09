import logging
from datetime import datetime

from django.db.transaction import atomic, DatabaseError
from django.utils.timezone import make_aware
from celery import current_app as app

from datagrowth.configuration import create_config
from datagrowth.resources.http.tasks import send
from datagrowth.utils.iterators import ibatch

from harvester.tasks.base import DatabaseConnectionResetTask
from harvester.utils.extraction import get_harvest_seeds
from core.constants import Repositories, HarvestStages
from core.models import Harvest, Dataset, DatasetVersion


logger = logging.getLogger("harvester")


@app.task(name="sync_sharekit_metadata", base=DatabaseConnectionResetTask)
def sync_sharekit_metadata():
    # Select which data to sync this run
    latest_active_dataset = Dataset.objects.filter(is_active=True).last()
    if not latest_active_dataset:
        return
    dataset_version = DatasetVersion.objects.get_current_version()
    harvest_queryset = Harvest.objects.filter(
        dataset=latest_active_dataset,
        source__repository=Repositories.SHAREKIT,
        stage=HarvestStages.COMPLETE  # prevents syncing materials half way a full harvest
    )
    # First we acquire a permanent lock on Harvests,
    # because if latest_update_at is a while ago this command will run a long time.
    # We don't want to keep all those syncing changes waiting in that one transaction.
    try:
        with atomic():
            harvest_queryset.filter(is_syncing=False).select_for_update(nowait=True).update(is_syncing=True)
    except DatabaseError:
        logger.warning("Did not acquire lock on Harvester when syncing Sharekit metadata")
        return
    # Now that we're the only ones starting the sync we execute it
    for harvest in harvest_queryset.filter(is_syncing=True):
        # Check that a non-valid harvest source didn't slip through the lock
        if harvest.stage != HarvestStages.COMPLETE:
            logging.warning("Encountered a non-complete harvest source during sync")
            continue
        # Recording which time will become latest_update_at
        current_time = make_aware(datetime.now())
        # Getting metadata from Sharekit and stop immediately if anything went wrong
        send_config = create_config("http_resource", {
            "resource": harvest.source.repository,
            "continuation_limit": 10000,
        })
        set_specification = harvest.source.spec
        scc, err = send(
            set_specification, f"{harvest.latest_update_at:%Y-%m-%dT%H:%M:%SZ}",
            config=send_config,
            method="get"
        )
        if len(err) or not len(scc):
            continue
        # Now parse the metadata and update current Collection for this Harvest
        seeds = get_harvest_seeds(
            Repositories.SHAREKIT,
            set_specification,
            harvest.latest_update_at,
            include_no_url=True
        )
        collection = dataset_version.collection_set.get(name=harvest.source.spec)
        for seeds_batch in ibatch(seeds, batch_size=32):
            updates = []
            for seed in seeds_batch:
                # We never sync the language because we would have to switch a document between indices.
                # A delete signal would also not propagate, because language will be None
                # and that maps to latest-unk index, but the document might be elsewhere.
                # During the nightly harvest the indices get recreated and a language switch will propagate.
                seed.pop("language", None)
                updates.append(seed)
            collection.update(updates, "external_id")
        # Last but not least we update the harvest update time to get a different delta later
        harvest.latest_update_at = current_time
        harvest.save()
    # And we release the syncing lock
    with atomic():
        harvest_queryset.filter(is_syncing=True).select_for_update().update(is_syncing=False)
