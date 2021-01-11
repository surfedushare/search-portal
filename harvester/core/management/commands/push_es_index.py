from django.conf import settings
from datetime import datetime
from dateutil import tz

from core.models import Dataset, ElasticIndex
from core.management.base import HarvesterCommand
from harvester import logger


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
        begin_of_time = datetime(year=1970, month=1, day=1, tzinfo=tz.tzutc())
        earliest_harvest = begin_of_time if recreate else dataset.get_earliest_harvest_date() or begin_of_time

        logger.info(f"Upserting ES index for {dataset.name}", dataset=dataset.name)
        logger.info(
            f"since:{earliest_harvest:%Y-%m-%d}, recreate:{recreate} and promote:{promote}", dataset=dataset.name
        )

        lang_doc_dict = dataset.get_elastic_documents_by_language(since=earliest_harvest)
        for lang in lang_doc_dict.keys():
            logger.info(f'{lang}:{len(lang_doc_dict[lang])}', dataset=dataset.name)

        for lang, docs in lang_doc_dict.items():
            if lang == "unk":
                logger.warning(
                    f"Found arrangements with ambiguous language {[doc['_id'] for doc in docs]}",
                    dataset=dataset.name
                )
            if lang not in settings.ELASTICSEARCH_ANALYSERS:
                logger.warning(f"Found language not in analysers: {lang}", dataset=dataset.name)
                continue
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
                logger.info(f"Promoting index { index.remote_name } to latest", dataset=dataset.name)
                index.promote_to_latest()
            logger.info(f'{lang} errors:{index.error_count}', dataset=dataset.name)
