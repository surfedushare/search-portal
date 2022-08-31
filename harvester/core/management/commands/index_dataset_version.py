from django.urls import reverse

from core.models import Dataset, ElasticIndex, EducationalLevels
from core.management.base import PipelineCommand
from core.utils.notifications import send_admin_notification


class Command(PipelineCommand):

    command_name = "index_dataset_version"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-hv', '--harvester-version', type=str, default="")
        parser.add_argument('-np', '--no-promote', action="store_true")
        parser.add_argument('-se', '--skip-evaluation', action="store_true")

    def handle(self, *args, **options):

        dataset_name = options["dataset"]
        version = options["harvester_version"]
        should_promote = not options["no_promote"]
        skip_evaluation = options["skip_evaluation"] or version

        dataset = Dataset.objects.get(name=dataset_name)
        version_filter = {}
        if version:
            version_filter.update({"version": version})
        dataset_version = dataset.versions.filter(**version_filter).last()
        collection_errors = dataset.evaluate_dataset_version(dataset_version) if not skip_evaluation else []

        for collection in collection_errors:
            send_admin_notification(
                f"The {collection.name} collection dropped by more than 5%. Falling back to previous version.",
                reverse("admin:core_collection_changelist")
            )
            dataset_version.document_set.filter(collection__name=collection.name).update(dataset_version=None)
            dataset_version.copy_collection(collection)

        self.logger.start("index")
        for educational_level in EducationalLevels:
            self.logger.start(f"index.level.{educational_level}")
            self._create_index(dataset_version, educational_level, should_promote)
            self.logger.end(f"index.level.{educational_level}")
        self.logger.end("index")

    def _create_index(self, dataset_version, educational_level, should_promote):
        lang_doc_dict = dataset_version.get_search_documents_by_language(minimal_educational_level=educational_level)
        for lang in lang_doc_dict.keys():
            self.logger.info(f'{lang}:{len(lang_doc_dict[lang])}')

        for lang in ["nl", "en", "unk"]:
            self.logger.start(f"index.{lang}")
            index, created = ElasticIndex.objects.get_or_create(
                name=f"{dataset_version.dataset.name}-{dataset_version.version}-{dataset_version.id}",
                language=lang,
                educational_level=educational_level,
                defaults={
                    "dataset_version": dataset_version,
                    "configuration": ElasticIndex.get_index_config(lang)
                }
            )
            index.configuration = None  # gets recreated by the clean method below
            index.clean()
            index.save()
            errors = index.push(lang_doc_dict[lang], recreate=True)
            self.logger.open_search_errors(errors)
            if should_promote:
                self.logger.info(f"Promoting index { index.remote_name } to latest")
                index.promote_to_latest()
            self.logger.end(f"index.{lang}", fail=index.error_count)

        if should_promote:
            dataset_version.set_current()
