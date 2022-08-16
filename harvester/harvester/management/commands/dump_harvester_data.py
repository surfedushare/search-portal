import os
import logging
from invoke import Context

from django.conf import settings
from django.core.management import base, call_command
from datagrowth.utils import get_dumps_path, object_to_disk, queryset_to_disk

from harvester.settings import environment
from core.models import (Dataset, HttpTikaResource, Extension, ExtructResource, YoutubeThumbnailResource,
                         PdfThumbnailResource)
from metadata.models import MetadataValue, MetadataField, MetadataTranslation
from edurep.models import EdurepOAIPMH
from sharekit.models import SharekitMetadataHarvest


logger = logging.getLogger("harvester")


class Command(base.LabelCommand):

    resources = [
        "core.HttpTikaResource",
        "core.ExtructResource",
        "core.YoutubeThumbnailResource",
        "core.PdfThumbnailResource",
        "sharekit.SharekitMetadataHarvest",
        "metadata.MetadataField",
        "metadata.MetadataTranslation",
        "metadata.MetadataValue"
    ]

    def dump_resources(self):
        paths = []
        for resource_model in self.resources:
            clazz_name = resource_model.split(".")[1]
            clazz = globals()[clazz_name]
            dump_file = os.path.join(get_dumps_path(clazz), f"{clazz.get_name()}.dump.json")
            paths.append(dump_file)
            print(f"Dumping {clazz_name} to {dump_file}")
            call_command("dump_resource", resource_model)

        return paths

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-de', '--download-edurep', action="store_true")

    def handle_label(self, dataset_label, **options):
        download_edurep = options["download_edurep"]
            
        dataset = Dataset.objects.get(name=dataset_label)

        destination = get_dumps_path(dataset)
        if not os.path.exists(destination):
            os.makedirs(destination)
        dataset_file = os.path.join(destination, "{}.{}.json".format(dataset.name, dataset.id))
        with open(dataset_file, "w") as json_file:
            object_to_disk(dataset, json_file)
            queryset_to_disk(dataset.harvestsource_set, json_file)
            queryset_to_disk(dataset.harvest_set, json_file)
            queryset_to_disk(dataset.versions.filter(is_current=True), json_file)
            for version in dataset.versions.filter(is_current=True):
                queryset_to_disk(version.indices, json_file)
                queryset_to_disk(version.collection_set, json_file)
                queryset_to_disk(version.document_set, json_file)
            queryset_to_disk(Extension.objects.all(), json_file)

        if download_edurep:
            self.resources.append("edurep.EdurepOAIPMH")

        resource_files = self.dump_resources()

        # Sync files with AWS
        if environment.env != "localhost":
            logger.info("Uploading files to AWS")
            ctx = Context(environment)
            harvester_data_bucket = f"s3://{environment.aws.harvest_content_bucket}/datasets/harvester"
            for file in [dataset_file] + resource_files:
                remote_file = harvester_data_bucket + file.replace(settings.DATAGROWTH_DATA_DIR, "", 1)
                ctx.run(f"aws s3 cp {file} {remote_file}", echo=True)

