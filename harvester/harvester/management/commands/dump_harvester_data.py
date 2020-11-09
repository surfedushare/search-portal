import os
from invoke import Context

from django.conf import settings
from django.core.management import base, call_command
from datagrowth.utils import get_dumps_path, object_to_disk, queryset_to_disk

from harvester.settings import environment
from core.management.base import HarvesterCommand
from core.models import Dataset
from edurep.models import EdurepOAIPMH


class Command(base.LabelCommand, HarvesterCommand):

    def dump_resources(self):
        call_command("dump_resource", "edurep.EdurepOAIPMH")
        edurep_oaipmh_file_path = os.path.join(
            get_dumps_path(EdurepOAIPMH),
            f"{EdurepOAIPMH.get_name()}.dump.json"
        )
        return [
            edurep_oaipmh_file_path
        ]

    def handle_label(self, dataset_label, **options):

        dataset = Dataset.objects.get(name=dataset_label)

        destination = get_dumps_path(dataset)
        if not os.path.exists(destination):
            os.makedirs(destination)
        dataset_file = os.path.join(destination, "{}.{}.json".format(dataset.name, dataset.id))
        with open(dataset_file, "w") as json_file:
            object_to_disk(dataset, json_file)
            queryset_to_disk(dataset.oaipmhset_set, json_file)
            queryset_to_disk(dataset.oaipmhharvest_set, json_file)
            queryset_to_disk(dataset.indices, json_file)
            queryset_to_disk(dataset.collection_set, json_file)
            queryset_to_disk(dataset.arrangement_set, json_file)
            queryset_to_disk(dataset.document_set, json_file)

        resource_files = self.dump_resources()

        # Sync files with AWS
        self.info("Uploading files to AWS")
        ctx = Context(environment)
        harvester_data_bucket = "s3://edushare-data/datasets/harvester"
        for file in [dataset_file] + resource_files:
            remote_file = harvester_data_bucket + file.replace(settings.DATAGROWTH_DATA_DIR, "", 1)
            ctx.run(f"aws s3 cp {file} {remote_file}", echo=True)
