import factory
from datetime import datetime

from core.models import (Document, Collection, Dataset, DatasetVersion, Harvest, HarvestSource, ElasticIndex,
                         FileResource, TikaResource)
from core.constants import HarvestStages, Repositories, DeletePolicies


class DatasetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Dataset

    name = "test"
    is_active = True


class DatasetVersionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DatasetVersion

    version = "0.0.1"
    is_current = True
    dataset = factory.SubFactory(DatasetFactory)
    created_at = datetime.now()


class ElasticIndexFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ElasticIndex


class CollectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Collection


class DocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Document

    class Params:
        title = "Zorgwekkend gedrag"
        file_type = "text"
        from_youtube = False
        analysis_allowed = True
        mime_type = "text/html"
        pipeline = {}
        preview_path = None
        url = "https://maken.wikiwijs.nl/124977/Zorgwekkend_gedrag___kopie_1"
        language = "nl"

    dataset_version = factory.SubFactory(DatasetVersionFactory)
    reference = factory.Sequence(lambda n: "surf:oai:sufsharekit.nl:{}".format(n))
    properties = factory.LazyAttribute(
        lambda o: {
            "external_id": o.reference,
            "title": o.title,
            "file_type": o.file_type,
            "from_youtube": o.from_youtube,
            "analysis_allowed": o.analysis_allowed,
            "mime_type": o.mime_type,
            "files": [
                [
                    o.mime_type,
                    o.url,
                    "URL 1"
                ]
            ],
            "pipeline": o.pipeline,
            "preview_path": o.preview_path,
            "url": o.url,
            "language": {"metadata": o.language},
            "disciplines": [],
            "educational_levels": [],
            "lom_educational_levels": [],
            "authors": [],
            "publishers": [],
            "description": "Gedrag is zorgwekkend",
            "publisher_date": None,
            "copyright": "cc-by-40",
            "copyright_description": "http://creativecommons.org/licenses/by/4.0/",
            "aggregation_level": "2",
            "text": "blabla",
        })


class HarvestSourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HarvestSource

    name = "SURF Sharekit"
    repository = Repositories.EDUREP
    spec = "surf"
    delete_policy = DeletePolicies.TRANSIENT


class HarvestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Harvest

    dataset = factory.SubFactory(DatasetFactory)
    source = factory.SubFactory(HarvestSourceFactory)
    stage = HarvestStages.NEW


class FileResourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FileResource

    uri = "https://maken.wikiwijs.nl/124977/Zorgwekkend_gedrag___kopie_1"


class TikaResourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TikaResource

    uri = "java -J -jar -t http://localhost:8000/media/harvester/core/downloads/f/78/20200213173646291110." \
          "Zorgwekkend_gedrag___kopie_1 tika-app-1.25.jar"
