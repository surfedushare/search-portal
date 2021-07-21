from collections import defaultdict

from django.core.management import CommandError
from django.utils.timezone import now
from datagrowth.resources.http.tasks import send
from datagrowth.configuration import create_config

from core.management.base import PipelineCommand
from core.constants import HarvestStages
from core.models import Harvest, DatasetVersion, Collection, Document
from harvester.utils.extraction import get_harvest_seeds


class Command(PipelineCommand):

    command_name = "harvest_metadata"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-r', '--repository', action="store")

    def harvest_seeds(self, harvest, current_time):
        send_config = create_config("http_resource", {
            "resource": harvest.source.repository,
            "continuation_limit": 10000,
        })

        set_specification = harvest.source.spec
        scc, err = send(set_specification, f"{harvest.latest_update_at:%Y-%m-%d}", config=send_config, method="get")

        if len(err):
            raise CommandError(f"Failed to harvest seeds from {harvest.source.name}")

        harvest.harvested_at = current_time
        harvest.save()

        return len(scc), len(err)

    def preprocess_seeds(self, harvest_queryset):
        self.logger.start("preprocess")
        seeds_by_collection = defaultdict(list)
        source_count = harvest_queryset.count()
        for harvest in harvest_queryset:
            set_specification = harvest.source.spec
            upserts = []
            deletes = []
            for seed in get_harvest_seeds(set_specification, harvest.latest_update_at, include_no_url=True):
                if seed.get("state", "active") == "active":
                    upserts.append(seed)
                else:
                    deletes.append(seed)
            seeds_by_collection[(harvest.source.repository, harvest.source.spec)] += (upserts, deletes,)
            self.logger.progress(f"preprocess.{set_specification}", source_count, success=len(upserts) + len(deletes))
        self.logger.end("preprocess")
        return seeds_by_collection

    def handle_upsert_seeds(self, collection, seeds):
        self.logger.start("documents.upsert")
        documents_count = 0
        for seeds_batch in self.batchify("documents.upsert", seeds, len(seeds)):
            seeds = list(seeds_batch)
            existing_documents = {
                reference: identifier
                for reference, identifier in Document.objects.filter(
                    reference__in=[seed["external_id"] for seed in seeds if seed["external_id"]],
                    collection=collection
                ).values_list("reference", "id")
            }
            updates = []
            inserts = []
            for seed in seeds:
                self.logger.report_material(seed["external_id"], title=seed["title"], url=seed["url"])
                document = Document.objects.build_from_seed(
                    seed,
                    collection=collection,
                    metadata_pipeline_key="seed_resource"
                )
                if document.reference in existing_documents:
                    document.id = existing_documents[document.reference]
                    document.modified_at = now()
                    updates.append(document)
                else:
                    inserts.append(document)
            Document.objects.bulk_create(inserts)
            Document.objects.bulk_update(updates, ["properties", "modified_at"])
            documents_count += len(updates)
            documents_count += len(inserts)

        self.logger.end("documents.upsert", success=documents_count, fail=0)
        return documents_count

    def handle_deletion_seeds(self, collection, deletion_seeds):
        self.logger.start("documents.delete")
        document_delete_total = 0
        for seeds_batch in self.batchify("update.delete.batch", deletion_seeds, len(deletion_seeds)):
            ids = [seed["external_id"] for seed in seeds_batch]
            for external_id in ids:
                self.logger.report_material(external_id, state="delete")
            delete_total, delete_details = collection.documents.filter(reference__in=ids).delete()
            document_delete_total += delete_total
        self.logger.end("update.delete", success=document_delete_total)
        return document_delete_total

    def handle(self, *args, **options):

        dataset_name = options["dataset"]
        dataset_version = DatasetVersion.objects.filter(dataset__name=dataset_name, is_current=True).last()
        repository_resource = options["repository"]
        repository, resource = repository_resource.split(".")
        harvest_phase = f"seeds.{repository}"

        self.logger.start(harvest_phase)

        harvest_queryset = Harvest.objects.filter(
            dataset__name=dataset_name,
            stage=HarvestStages.NEW,
            source__repository=repository_resource
        )
        if not harvest_queryset.exists():
            self.logger.end(harvest_phase, success=0, fail=0)
            return

        # Calling the Resources to get meta data about learning materials
        current_time = now()
        total_success_count = 0
        total_fail_count = 0
        sources_count = harvest_queryset.count()

        for harvest in harvest_queryset:
            success_count, error_count = self.harvest_seeds(harvest, current_time)
            set_specification = harvest.source.spec
            total_success_count += success_count
            total_fail_count += error_count
            self.logger.progress(f"{harvest_phase}.{set_specification}", total=sources_count, success=success_count,
                                 fail=error_count)

        self.logger.end(harvest_phase, total_success_count, total_fail_count)

        # Processing the meta data into Documents
        for info, seeds in self.preprocess_seeds(harvest_queryset).items():
            # Unpacking
            repository, spec_name = info
            upserts, deletes = seeds
            # Get or create the collection these seeds belong to
            collection, created = Collection.objects.get_or_create(
                name=spec_name,
                dataset_version=dataset_version,
                defaults={
                    "referee": "external_id"
                }
            )
            if created:
                self.logger.debug(f"Created collection '{spec_name}'")
            else:
                self.logger.debug(f"Adding to existing collection '{spec_name}'")

            self.handle_upsert_seeds(collection, upserts)
            self.handle_deletion_seeds(collection, deletes)
            self.logger.report_results(spec_name, repository, collection.document_set.count())
