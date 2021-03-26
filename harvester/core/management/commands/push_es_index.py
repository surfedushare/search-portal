from django.conf import settings
from datetime import datetime
from dateutil import tz

from core.models import Dataset, ElasticIndex
from core.management.base import PipelineCommand


class Command(PipelineCommand):

    command_name = "push_es_index"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-r', '--recreate', action="store_true")
        parser.add_argument('-p', '--promote', action="store_true")

    def handle(self, *args, **options):

        dataset = Dataset.objects.get(name=options["dataset"])
        recreate = options["recreate"]
        promote = options["promote"]
        begin_of_time = datetime(year=1970, month=1, day=1, tzinfo=tz.tzutc())
        earliest_harvest = begin_of_time if recreate else dataset.get_earliest_harvest_date() or begin_of_time

        self.logger.start("index")
        self.logger.info(f"since:{earliest_harvest:%Y-%m-%d}, recreate:{recreate} and promote:{promote}")

        lang_doc_dict = dataset.get_elastic_documents_by_language(since=earliest_harvest)
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
                name=dataset.name,
                language=lang,
                defaults={
                    "dataset": dataset,
                    "configuration": ElasticIndex.get_index_config(lang)
                }
            )
            if recreate:
                index.configuration = None  # gets recreated by the clean method below
            index.clean()
            index.push(docs, recreate=recreate)
            index.save()
            if promote or recreate:
                self.logger.info(f"Promoting index { index.remote_name } to latest")
                index.promote_to_latest()
            self.logger.end(f"index.{lang}", fail=index.error_count)

        self.logger.end("index")
