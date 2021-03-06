from collections import defaultdict
from django.db.models import Count

from datagrowth.utils import ibatch
from core.models import Dataset, Collection, Arrangement, OAIPMHHarvest
from core.constants import HarvestStages
from core.management.base import OutputCommand
from core.utils.resources import get_material_resources, get_basic_material_resources, serialize_resource
from edurep.utils import get_edurep_oaipmh_seeds
from harvester import logger


class Command(OutputCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-d', '--dataset', type=str, required=True)

    def get_documents_from_transcription(self, transcription_resource, metadata, pipeline):
        if transcription_resource is None or not transcription_resource.success:
            # TODO: as long as Amber is not implemented we return empty documents for transcriptions
            return [self._create_document(
                "",
                meta=metadata,
                pipeline=pipeline,
                file_type="video",
                identifier_postfix="video"
            )]
        _, transcript = transcription_resource.content
        return [self._create_document(
            transcript,
            meta=metadata,
            pipeline=pipeline,
            file_type="video",
            identifier_postfix="video"
        )]

    def get_documents_from_zip(self, file_resource, tika_resource, metadata, pipeline):
        tika_content_type, data = tika_resource.content
        if data is None:
            return []
        text = data.get("X-TIKA:content", "")
        return [self._create_document(
            text,
            meta=metadata,
            pipeline=pipeline
        )]

    def get_documents(self, file_resource, tika_resource, metadata, pipeline):
        text = ""
        if tika_resource is None or not tika_resource.success:
            return [self._create_document(text, meta=metadata, pipeline=pipeline)]
        if tika_resource.is_zip():
            return self.get_documents_from_zip(file_resource, tika_resource, metadata, pipeline)
        tika_content_type, data = tika_resource.content
        if data is None:
            return [self._create_document(text, meta=metadata, pipeline=pipeline)]
        if not metadata.get("from_youtube"):
            text = data.get("X-TIKA:content", "")
        return [self._create_document(text, meta=metadata, pipeline=pipeline)]

    def handle_upsert_seeds(self, collection, seeds):
        skipped = 0
        dumped = 0
        documents_count = 0
        logger.info(f"Upserting for {collection.name}...", dataset=collection.dataset.name)
        for seed in self.progress(seeds):
            file_resource, tika_resource, video_resource, transcription_resource = \
                get_material_resources(seed["url"], seed.get("title", None))
            pipeline = {
                "file": serialize_resource(file_resource),
                "tika": serialize_resource(tika_resource),
                "video": serialize_resource(video_resource),
                "kaldi": serialize_resource(transcription_resource)
            }
            document_resource = tika_resource
            is_package = "package_url" in seed
            if is_package:
                package_file_resource, package_tika_resource = get_basic_material_resources(seed["package_url"])
                pipeline.update({
                    "package_file": serialize_resource(package_file_resource),
                    "package_tika": serialize_resource(package_tika_resource),
                })
                document_resource = package_tika_resource
            has_video = tika_resource.has_video() if tika_resource is not None else False

            documents = []
            documents += self.get_documents(file_resource, document_resource, seed, pipeline)
            if has_video:
                documents += self.get_documents_from_transcription(transcription_resource, seed, pipeline)

            if not len(documents):
                logger.debug(
                    f"Skipped material with external id '{seed['external_id']}'",
                    dataset=collection.dataset
                )
                skipped += 1
                continue
            dumped += 1

            reference_id = seed["external_id"]
            arrangement, created = Arrangement.objects.get_or_create(
                meta__reference_id=reference_id,
                dataset=collection.dataset,
                collection=collection,
                defaults={"referee": "id"}
            )
            arrangement.meta.update({
                "reference_id": reference_id,
                "is_package": is_package,
                "url": seed["url"],
                "keywords": seed.get("keywords", []),
            })
            arrangement.save()
            arrangement.update(documents, "id", validate=False, collection=collection)
            arrangement.store_language()
            documents_count += len(documents)

        logger.info(f"Skipped URL's for {collection.name} during dump: {skipped}", dataset=collection.dataset.name)
        logger.info(f"Dumped Arrangements for {collection.name}: {dumped}", dataset=collection.dataset.name)
        logger.info(f"Dumped Documents for {collection.name}: {documents_count}", dataset=collection.dataset.name)

        return skipped, dumped, documents_count

    def handle_deletion_seeds(self, collection, deletion_seeds):
        logger.info(f"Deleting for {collection.name} ...")
        document_delete_total = 0
        for seeds in ibatch(deletion_seeds, 32, progress_bar=self.show_progress):
            ids = [seed["external_id"] for seed in seeds]
            for external_id in ids:
                for doc in collection.documents.filter(collection=collection,
                                                       properties__contains={"external_id": external_id}):
                    doc.delete()
                    document_delete_total += 1
        arrangement_delete_count = 0
        for arrangement in Arrangement.objects.annotate(num_docs=Count('document')) \
                .filter(collection=collection, num_docs=0):
            arrangement.delete()
            arrangement_delete_count += 1

        logger.info(
            f"Deleted Arrangements for {collection.name}: {arrangement_delete_count}", dataset=collection.dataset.name
        )
        logger.info(
            f"Deleted Documents for {collection.name}: {document_delete_total}", dataset=collection.dataset.name
        )

        return arrangement_delete_count, document_delete_total

    def handle(self, *args, **options):

        dataset_name = options["dataset"]
        dataset = Dataset.objects.get(name=dataset_name)

        harvest_queryset = OAIPMHHarvest.objects.filter(
            dataset__name=dataset_name,
            stage=HarvestStages.VIDEO
        )
        if not harvest_queryset.exists():
            raise OAIPMHHarvest.DoesNotExist(
                f"There are no scheduled and VIDEO EdurepHarvest objects for '{dataset_name}'"
            )

        logger.info(f"Update dataset for {dataset_name}", dataset=dataset_name)

        logger.info("Extracting data from sources...", dataset=dataset_name)

        seeds_by_collection = defaultdict(list)
        for harvest in self.progress(harvest_queryset, total=harvest_queryset.count()):
            set_specification = harvest.source.spec
            upserts = []
            deletes = []
            for seed in get_edurep_oaipmh_seeds(set_specification, harvest.latest_update_at, include_no_url=True):
                if seed.get("state", "active") == "active":
                    upserts.append(seed)
                else:
                    deletes.append(seed)
            seeds_by_collection[harvest.source.spec] += (upserts, deletes,)
            logger.info(
                f"Files of collection '{harvest.source.spec} considered for processing, "
                f"upserts:{len(upserts)} deletes:{len(deletes)}",
                dataset=dataset_name,
                aggregate={"upserts": len(upserts), "deletes": len(deletes)}
            )

        for spec_name, seeds in seeds_by_collection.items():
            # Unpacking seeds
            upserts, deletes = seeds

            # Get or create the collection these seeds belong to
            collection, created = Collection.objects.get_or_create(name=spec_name, dataset=dataset)
            collection.referee = "id"
            collection.save()
            if created:
                logger.info(f"Created collection '{spec_name}'", dataset=dataset_name)
            else:
                logger.info(f"Adding to existing collection '{spec_name}'", dataset=dataset_name)

            self.handle_upsert_seeds(collection, upserts)
            self.handle_deletion_seeds(collection, deletes)

        harvest_queryset.update(stage=HarvestStages.PREVIEW)

        logger.info("Finished updating the dataset", dataset=dataset_name)
