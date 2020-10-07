from django.conf import settings
from datetime import datetime
from dateutil import tz

from core.models import Dataset, ElasticIndex
from core.management.base import HarvesterCommand


class Command(HarvesterCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-d', '--dataset', type=str, required=True)
        parser.add_argument('-r', '--recreate', action="store_true")
        parser.add_argument('-p', '--promote', action="store_true")

    def handle(self, *args, **options):

        dataset = Dataset.objects.get(name=options["dataset"])
        recreate = options["recreate"]
        promote = options["promote"]
        earliest_harvest = dataset.get_earliest_harvest_date() or datetime(year=1970, month=1, day=1, tzinfo=tz.tzutc())

        self.info(f"Upserting ES index for {dataset.name}")
        self.info(f"since:{earliest_harvest:%Y-%m-%d}, recreate:{recreate} and promote:{promote}")

        lang_doc_dict = dataset.get_elastic_documents_by_language(since=earliest_harvest)
        for lang in lang_doc_dict.keys():
            self.info(f'{lang}:{len(lang_doc_dict[lang])}')

        for lang, docs in lang_doc_dict.items():
            if lang == "unk":
                self.info("Found arrangements with ambiguous language", [doc["_id"] for doc in docs])
            if lang not in settings.ELASTICSEARCH_ANALYSERS:
                continue
            index, created = ElasticIndex.objects.get_or_create(
                name=dataset.name,
                language=lang,
                defaults={
                    "dataset": dataset,
                    "configuration": ElasticIndex.get_index_config(lang)
                }
            )
            index.clean()
            index.push(docs, recreate=recreate)
            index.save()
            if promote or recreate:
                self.info(f"Promoting index { index.remote_name } to latest")
                index.promote_to_latest()
            self.info(f'{lang} errors:{index.error_count}')
