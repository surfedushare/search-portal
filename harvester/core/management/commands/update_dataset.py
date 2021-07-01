from mimetypes import guess_type
from collections import defaultdict

from django.conf import settings
from django.db.models import F

from core.models import DatasetVersion, Collection, Document, Harvest
from core.constants import HarvestStages
from core.management.base import PipelineCommand
from core.utils.resources import get_material_resources, serialize_resource
from core.utils.language import get_language_from_snippet
from harvester.utils.extraction import get_harvest_seeds


class Command(PipelineCommand):

    command_name = "update_dataset"

    def _create_document(self, text, meta, pipeline=None):

        url = meta.get("url", None)
        mime_type = meta.get("mime_type", None)
        if mime_type is None and url:
            mime_type, encoding = guess_type(url)

        identifier = meta["external_id"]

        text_language = get_language_from_snippet(text)
        title = meta.get("title", None)
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
            "file_type": settings.MIME_TYPE_TO_FILE_TYPE.get(mime_type, "unknown"),
            "technical_type": meta.get("technical_type", None),
            "material_type": meta.get("material_type", None),
            "mime_type": mime_type,
            "files": meta.get("files", []),
            "authors": meta.get("authors", []),
            "publishers": meta.get("publishers", []),
            "description": meta.get("description", None),
            "copyright": meta.get("copyright", None),
            "copyright_description": meta.get("copyright_description", None),
            "aggregation_level": meta.get("aggregation_level", None),
            "publisher_date": meta.get("publisher_date", None),
            "disciplines": meta.get("disciplines", []),
            "preview_path": meta.get("preview_path", None),
            "lom_educational_levels": meta.get("lom_educational_levels", []),
            "lowest_educational_level": meta.get("lowest_educational_level", -1),
            "from_youtube": meta.get("from_youtube", False),
            "suggest": title,
            "pipeline": pipeline,
            "analysis_allowed": meta.get("analysis_allowed", False),
            "keywords": meta.get("keywords", []),
            "is_part_of": meta.get("is_part_of", []),
            "has_parts": meta.get("has_parts", []),
            "ideas": meta.get("ideas", []),
            "doi": meta.get("doi", None),
        }

    def get_documents_from_zip(self, file_resource, tika_resource, metadata, pipeline):
        tika_content_type, data = tika_resource.content
        if data is None:
            return []
        text = data.get("X-TIKA:content", "")
        return self._create_document(
            text,
            meta=metadata,
            pipeline=pipeline
        )

    def get_document(self, file_resource, tika_resource, metadata, pipeline):
        text = ""
        if tika_resource is None or not tika_resource.success:
            return self._create_document(text, meta=metadata, pipeline=pipeline)
        if tika_resource.is_zip():
            return self.get_documents_from_zip(file_resource, tika_resource, metadata, pipeline)
        tika_content_type, data = tika_resource.content
        if data is None:
            return self._create_document(text, meta=metadata, pipeline=pipeline)
        if not metadata.get("from_youtube"):
            text = data.get("X-TIKA:content", "")
        return self._create_document(text, meta=metadata, pipeline=pipeline)

    def handle_upsert_seeds(self, collection, seeds):
        skipped = 0
        documents_count = 0
        self.logger.start("update.upsert")
        for seed in seeds:
            file_resource, tika_resource, video_resource, transcription_resource = \
                get_material_resources(seed["url"], seed.get("title", None))
            pipeline = {
                "file": serialize_resource(file_resource),
                "tika": serialize_resource(tika_resource),
            }
            properties = self.get_document(file_resource, tika_resource, seed, pipeline)

            reference_id = seed["external_id"]
            document, created = Document.objects.get_or_create(
                reference=reference_id,
                dataset_version=collection.dataset_version,
                collection=collection,
                defaults={"properties": properties}
            )
            if not created:
                document.properties = properties
                document.save()

            documents_count += 1
            self.logger.report_material(seed["external_id"], title=seed["title"], url=seed["url"], pipeline=pipeline)

        self.logger.end("update.upsert", success=documents_count, fail=skipped)

        return skipped, documents_count

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
        self.logger.end("update.delete", success=document_delete_total)
        return document_delete_total

    def handle(self, *args, **options):

        dataset_name = options["dataset"]
        dataset_version = DatasetVersion.objects.filter(dataset__name=dataset_name, is_current=True).last()

        harvest_queryset = Harvest.objects.filter(
            dataset__name=dataset_name,
            stage=HarvestStages.VIDEO
        )
        if not harvest_queryset.exists():
            raise Harvest.DoesNotExist(
                f"There are no scheduled and VIDEO Harvest objects for '{dataset_name}'"
            )

        self.logger.start("update")
        self.logger.start("update.sourcing")

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
            self.logger.progress("update.sourcing", source_count, success=len(upserts) + len(deletes))

        self.logger.end("update.sourcing")

        for info, seeds in seeds_by_collection.items():
            # Unpacking
            repository, spec_name = info
            upserts, deletes = seeds

            # Get or create the collection these seeds belong to
            collection, created = Collection.objects.get_or_create(name=spec_name, dataset_version=dataset_version)
            collection.referee = "id"
            collection.save()
            if created:
                self.logger.debug(f"Created collection '{spec_name}'")
            else:
                self.logger.debug(f"Adding to existing collection '{spec_name}'")

            self.handle_upsert_seeds(collection, upserts)
            self.handle_deletion_seeds(collection, deletes)
            self.logger.report_results(spec_name, repository, collection.document_set.count())

        harvest_queryset.update(stage=HarvestStages.PREVIEW, latest_update_at=F("harvested_at"))

        self.logger.end("update")
