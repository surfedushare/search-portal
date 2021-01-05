import factory

from core.models import Document, Dataset, OAIPMHHarvest, OAIPMHSet, FileResource
from core.constants import HarvestStages


class DatasetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Dataset

    name = "epsilon"
    is_active = True


class DocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Document

    class Params:
        file_type = "text"
        from_youtube = False
        mime_type = "text/html"
        pipeline = {}
        preview_path = None
        url = "https://maken.wikiwijs.nl/124977/Zorgwekkend_gedrag___kopie_1"

    dataset = factory.SubFactory(DatasetFactory)
    reference = factory.Sequence(lambda n: "surf:oai:sufsharekit.nl:{}".format(n))
    properties = factory.LazyAttribute(
        lambda o: {
            "file_type": o.file_type,
            "from_youtube": o.from_youtube,
            "mime_type": o.mime_type,
            "pipeline": o.pipeline,
            "preview_path": o.preview_path,
            "url": o.url
        })


class OAIPMHSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OAIPMHSet

    name = "SURF Sharekit"
    repository = "edurep.EdurepOAIPMH"
    spec = "surf"


class OAIPMHHarvestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OAIPMHHarvest

    dataset = factory.SubFactory(DatasetFactory)
    source = factory.SubFactory(OAIPMHSetFactory)
    stage = HarvestStages.NEW


class FileResourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FileResource

    uri = "https://maken.wikiwijs.nl/124977/Zorgwekkend_gedrag___kopie_1"
