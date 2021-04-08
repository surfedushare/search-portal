import factory

from core.models import Document, Dataset, DatasetVersion, Harvest, HarvestSource, FileResource
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
            "pipeline": o.pipeline,
            "preview_path": o.preview_path,
            "url": o.url
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
