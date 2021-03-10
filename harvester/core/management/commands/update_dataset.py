from mimetypes import guess_type
from collections import defaultdict

from django.db.models import Count
from django.conf import settings

from core.models import Dataset, Collection, Arrangement, OAIPMHHarvest
from core.constants import HarvestStages
from core.management.base import PipelineCommand
from core.utils.resources import get_material_resources, get_basic_material_resources, serialize_resource
from core.utils.language import get_language_from_snippet
from edurep.utils import get_edurep_oaipmh_seeds


class Command(PipelineCommand):

    command_name = "update_dataset"

    def _create_document(self, text, meta, title=None, url=None, mime_type=None, file_type=None, pipeline=None,
                         identifier_postfix=None):

        url = url or meta.get("url", None)
        mime_type = mime_type or meta.get("mime_type", None)
        if mime_type is None and url:
            mime_type, encoding = guess_type(url)
        file_type = file_type or settings.MIME_TYPE_TO_FILE_TYPE.get(mime_type, "unknown")

        identifier = meta["external_id"]
        if identifier_postfix:
            identifier += f":{identifier_postfix}"

        text_language = get_language_from_snippet(text)
        title = title or meta.get("title", None)
        title_language = get_language_from_snippet(title)
        meta_language = meta.get("language", None)

        pipeline = pipeline or {}
        assert isinstance(pipeline, dict), "Pipeline should be a dictionary got {} instead".format(type(pipeline))
        pipeline["harvest"] = settings.GIT_COMMIT

        return {
            "id": identifier,
            "external_id": meta["external_id"],
            "title": title,
            "language": {
                "metadata": meta_language,
                "from_text": text_language,
                "from_title": title_language
            },
            "url": url,
            "text": text,
            "file_type": file_type,
            "mime_type": mime_type,
            "author": meta.get("author", []),
            "authors": meta.get("authors", []),
            "publishers": meta.get("publishers", []),
            "description": meta.get("description", None),
            "copyright": meta.get("copyright", None),
            "aggregation_level": meta.get("aggregation_level", None),
            "publisher_date": meta.get("publisher_date", None),
            "disciplines": meta.get("disciplines", []),
            "educational_levels": meta.get("educational_levels", []),
            "preview_path": meta.get("preview_path", None),
            "lom_educational_levels": meta.get("lom_educational_levels", []),
            "lowest_educational_level": meta.get("lowest_educational_level", -1),
            "from_youtube": meta.get("from_youtube", False),
            "suggest": title,
            "pipeline": pipeline,
            "analysis_allowed": meta.get("analysis_allowed", False),
            "is_part_of": meta.get("is_part_of", None),
            "has_part": meta.get("has_part", []),
            "ideas": meta.get("ideas", [])
        }

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
        self.logger.start("update.upsert")
        for seed in seeds:
            file_resource, tika_resource, video_resource, transcription_resource = \
                get_material_resources(seed["url"], seed.get("title", None))
            pipeline = {
                "file": serialize_resource(file_resource),
                "tika": serialize_resource(tika_resource),
                "video": serialize_resource(video_resource),
                "kaldi": serialize_resource(transcription_resource)
            }
            has_video = tika_resource.has_video() if tika_resource is not None else False
            documents = self.get_documents(file_resource, tika_resource, seed, pipeline)
            if has_video:
                documents += self.get_documents_from_transcription(transcription_resource, seed, pipeline)

            if not len(documents):
                self.logger.debug(f"Skipped material with external id '{seed['external_id']}'")
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
                "url": seed["url"],
                "keywords": seed.get("keywords", []),
            })
            arrangement.save()
            arrangement.update(documents, "id", validate=False, collection=collection)
            arrangement.store_language()
            documents_count += len(documents)

            self.logger.report_material(seed["external_id"], title=seed["title"], url=seed["url"], pipeline=pipeline)

        self.logger.end("update.upsert", success=dumped, fail=skipped)

        return skipped, dumped, documents_count

    def handle_deletion_seeds(self, collection, deletion_seeds):
        self.logger.start("update.delete")
        document_delete_total = 0
        for seeds in self.batchify("update.delete.batch", deletion_seeds, len(deletion_seeds)):
            ids = [seed["external_id"] for seed in seeds]
            for external_id in ids:
                for doc in collection.documents.filter(collection=collection,
                                                       properties__contains={"external_id": external_id}):
                    self.logger.report_material(external_id, state="delete")
                    doc.delete()
                    document_delete_total += 1
        arrangement_delete_count = 0
        for arrangement in Arrangement.objects.annotate(num_docs=Count('document')) \
                .filter(collection=collection, num_docs=0):
            arrangement.delete()
            arrangement_delete_count += 1

        self.logger.end("update.delete", success=arrangement_delete_count)

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

        self.logger.start("update")
        self.logger.start("update.sourcing")

        seeds_by_collection = defaultdict(list)
        source_count = harvest_queryset.count()
        for harvest in harvest_queryset:
            set_specification = harvest.source.spec
            upserts = []
            deletes = []
            for seed in get_edurep_oaipmh_seeds(set_specification, harvest.latest_update_at, include_no_url=True):
                if seed.get("state", "active") == "active":
                    upserts.append(seed)
                else:
                    deletes.append(seed)
            seeds_by_collection[harvest.source.spec] += (upserts, deletes,)
            self.logger.progress("update.sourcing", source_count, success=len(upserts) + len(deletes))

        self.logger.end("update.sourcing")

        for spec_name, seeds in seeds_by_collection.items():
            # Unpacking seeds
            upserts, deletes = seeds

            # Get or create the collection these seeds belong to
            collection, created = Collection.objects.get_or_create(name=spec_name, dataset=dataset)
            collection.referee = "id"
            collection.save()
            if created:
                self.logger.debug(f"Created collection '{spec_name}'")
            else:
                self.logger.debug(f"Adding to existing collection '{spec_name}'")

            self.handle_upsert_seeds(collection, upserts)
            self.handle_deletion_seeds(collection, deletes)

        harvest_queryset.update(stage=HarvestStages.PREVIEW)

        self.logger.end("update")
