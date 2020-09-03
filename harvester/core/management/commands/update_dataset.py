from collections import defaultdict
from zipfile import BadZipFile

from django.core.exceptions import ValidationError
from django.db.models import Count

from datagrowth.utils import ibatch
from core.models import Dataset, Collection, Arrangement, OAIPMHHarvest
from core.constants import HarvestStages
from core.management.base import OutputCommand
from core.utils.resources import get_material_resources
from edurep.utils import get_edurep_oaipmh_seeds
from core.models import CommonCartridge


class Command(OutputCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-d', '--dataset', type=str, required=True)

    def get_documents_from_transcription(self, transcription_resource, metadata, pipeline):
        if transcription_resource is None or not transcription_resource.success:
            return []
        _, transcript = transcription_resource.content
        return [self._create_document(
            transcript,
            meta=metadata,
            pipeline=pipeline,
            file_type="video"
        )]

    def get_documents_from_zip(self, file_resource, tika_resource, metadata, pipeline):
        # Load zip as an IMS Common Cardridge
        # cc = CommonCartridge(file=file_resource.body)
        # try:
        #     cc.clean()
        # except (ValidationError, BadZipFile):
        #     self.warning(f"Invalid or missing common cartridge for file resource: {file_resource.id}")
        #     return []
        # Extract texts per file in the Common Cartridge
        # files = set()
        # texts_by_file = defaultdict(list)
        # for resource in cc.get_resources().values():
        #     files.update(resource["files"])
        tika_content_type, data = tika_resource.content
        if data is None:
            return False
        text = data.get("X-TIKA:content", "")
        # TODO: Tika is doing something different than before and isn't recursing files in packages
        # What happened and which settings will fix this?
        # current_file = None
        # for line in text.split("\n"):
        #     line = line.strip()
        #     if line in files:
        #         current_file = line
        #         continue
        #     if current_file and line:
        #         texts_by_file[current_file].append(line)
        # We temporarily disable creating multiple documents for a package
        # When there is a design to display courses in the portal we can re-enable this
        # Until that time concatenating all documents in a package to a single learning material
        # documents = {}
        # for file, texts in texts_by_file.items():
        #     doc = self._create_document(
        #         "\n".join(texts),
        #         url="{}/{}".format(metadata.get("package_url"), file),
        #         meta=metadata,
        #         pipeline=pipeline,
        #         hash_postfix=""  # updating URL to create unique hash instead, keeps legacy ids intact
        #     )
        #     documents[doc["id"]] = doc
        # return list(documents.values())
        # text = ""
        # for file, texts in texts_by_file.items():
        #     text += "\n".join(texts)
        return [self._create_document(
            text,
            url=metadata.get("package_url"),
            meta=metadata,
            pipeline=pipeline,
            hash_postfix=""  # updating URL to create unique hash instead, keeps legacy ids intact
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
        text = data.get("X-TIKA:content", "")
        return [self._create_document(text, meta=metadata, pipeline=pipeline)]

    def handle_upsert_seeds(self, collection, seeds):
        skipped = 0
        dumped = 0
        documents_count = 0
        self.info(f"Upserting for {collection.name} ...")
        for seed in self.progress(seeds):
            file_resource, tika_resource, video_resource, transcription_resource = \
                get_material_resources(seed["url"], seed.get("title", None))
            pipeline = {
                "file": self._serialize_resource(file_resource),
                "tika": self._serialize_resource(tika_resource),
                "video": self._serialize_resource(video_resource),
                "kaldi": self._serialize_resource(transcription_resource)
            }
            has_video = tika_resource.has_video() if tika_resource is not None else False

            documents = []
            documents += self.get_documents(file_resource, tika_resource, seed, pipeline)
            if has_video:
                documents += self.get_documents_from_transcription(transcription_resource, seed, pipeline)

            if not len(documents):
                skipped += 1
                continue
            dumped += 1

            reference_id = self.get_hash_from_url(seed["url"])
            arrangement, created = Arrangement.objects.get_or_create(
                meta__reference_id=reference_id,
                dataset=collection.dataset,
                collection=collection,
                defaults={"referee": "id"}
            )
            arrangement.meta.update({
                "reference_id": reference_id,
                "url": seed["url"],
                "keywords": seed.get("keywords", [])
            })
            arrangement.save()
            if len(documents):
                arrangement.update(documents, "id", validate=False, collection=collection)
                documents_count += len(documents)

        return skipped, dumped, documents_count

    def handle_deletion_seeds(self, collection, deletion_seeds):
        self.info(f"Deleting for {collection.name} ...")
        document_delete_total = 0
        for seeds in ibatch(deletion_seeds, 32, progress_bar=self.show_progress):
            ids = [seed["external_id"] for seed in seeds]
            for id in ids:
                for doc in collection.documents.filter(collection=collection, properties__contains={"external_id": id}):
                    doc.delete()
                    document_delete_total += 1
        arrangement_delete_count = 0
        for arrangement in Arrangement.objects.annotate(num_docs=Count('document')) \
                .filter(collection=collection, num_docs=0):
            arrangement.delete()
            arrangement_delete_count += 1
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

        self.header("CREATE OR UPDATE DATASET", options)

        self.info("Extracting data from sources ...")
        seeds_by_collection = defaultdict(list)
        for harvest in self.progress(harvest_queryset, total=harvest_queryset.count()):
            set_specification = harvest.source.spec
            upserts = []
            deletes = []
            for seed in get_edurep_oaipmh_seeds(set_specification, harvest.latest_update_at):
                if seed.get("state", "active") == "active":
                    upserts.append(seed)
                else:
                    deletes.append(seed)
            seeds_by_collection[harvest.source.spec] += (upserts, deletes,)
            self.info(f"Files considered for processing, upserts:{len(upserts)} deletes:{len(deletes)}")

        for spec_name, seeds in seeds_by_collection.items():
            # Unpacking seeds
            upserts, deletes = seeds

            # Get or create the collection these seeds belong to
            collection, created = Collection.objects.get_or_create(name=spec_name, dataset=dataset)
            collection.referee = "id"
            collection.save()
            if created:
                self.info("Created collection " + spec_name)
            else:
                self.info("Adding to collection " + spec_name)

            skipped, dumped, documents_count = self.handle_upsert_seeds(collection, upserts)
            deleted_arrangements, deleted_documents = self.handle_deletion_seeds(collection, deletes)

            self.info(f"Skipped URL's for {collection.name} during dump: {skipped}")
            self.info(f"Dumped Arrangements for {collection.name}: {dumped}")
            self.info(f"Dumped Documents for {collection.name}: {documents_count}")
            self.info(f"Deleted Arrangements for {collection.name}: {deleted_arrangements}")
            self.info(f"Deleted Documents for {collection.name}: {deleted_documents}")

        # Finish the dataset and harvest
        for harvest in harvest_queryset:
            harvest.stage = HarvestStages.COMPLETE
            harvest.save()
