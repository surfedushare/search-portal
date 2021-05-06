from django.conf import settings

from core.models import Dataset, ElasticIndex
from core.management.base import PipelineCommand


class Command(PipelineCommand):

    command_name = "index_dataset_version"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-hv', '--harvester-version', type=str, default="")
        parser.add_argument('-np', '--no-promote', action="store_true")

    def handle(self, *args, **options):

        dataset_name = options["dataset"]
        version = options["harvester_version"]
        should_promote = not options["no_promote"]

        dataset = Dataset.objects.get(name=dataset_name)
        version_filter = {"is_current": True}
        if version:
            version_filter.update({"version": version})
        dataset_version = dataset.versions.filter(**version_filter).last()

        self.logger.start("index")

        lang_doc_dict = dataset_version.get_elastic_documents_by_language()
        for lang in lang_doc_dict.keys():
            self.logger.info(f'{lang}:{len(lang_doc_dict[lang])}')

        for lang, docs in lang_doc_dict.items():
            if lang == "unk":
                self.logger.warning(
                    f"Found documents with ambiguous language {[doc['_id'] for doc in docs]}",
                )
            if lang not in settings.ELASTICSEARCH_ANALYSERS:
                self.logger.warning(f"Found language not in analysers: {lang}")
                continue

            self.logger.start(f"index.{lang}")

            index, created = ElasticIndex.objects.get_or_create(
                name=f"{dataset.name}-{dataset_version.version}-{dataset_version.id}",
                language=lang,
                defaults={
                    "dataset_version": dataset_version,
                    "configuration": ElasticIndex.get_index_config(lang)
                }
            )
            index.configuration = None  # gets recreated by the clean method below
            index.clean()
            index.push(docs, recreate=True)
            index.save()
            if should_promote:
                self.logger.info(f"Promoting index { index.remote_name } to latest")
                index.promote_to_latest()
            self.logger.end(f"index.{lang}", fail=index.error_count)

        self.logger.end("index")
