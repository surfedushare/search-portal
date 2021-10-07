from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from datagrowth.configuration import create_config
from datagrowth.resources.shell.tasks import run
from datagrowth.processors import Processor

from core.processors.pipeline.base import PipelineProcessor


class ShellPipelineProcessor(PipelineProcessor):

    def filter_documents(self, queryset):
        depends_on = self.config.pipeline_depends_on
        pipeline_phase = self.config.pipeline_phase
        filters = Q(**{f"pipeline__{depends_on}__success": True}) | Q(**{f"pipeline__{pipeline_phase}__success": False})
        return queryset.filter(filters)

    def process_batch(self, batch):

        config = create_config("shell_resource", self.config.retrieve_data)
        app_label, resource_model = config.resource.split(".")
        resource_type = ContentType.objects.get_by_natural_key(app_label, resource_model)

        updates = []
        creates = []
        for process_result in batch.processresult_set.all():
            args, kwargs = process_result.document.output(config.args, config.kwargs)
            successes, fails = run(*args, **kwargs, config=config)
            results = successes + fails
            if not len(results):
                continue
            result_id = results.pop(0)
            process_result.result_type = resource_type
            process_result.result_id = result_id
            updates.append(process_result)
            for result_id in results:
                # TODO: create docs here where necessary
                creates.append(
                    self.ProcessResult(document=process_result.document, batch=batch,
                                       result_id=result_id, result_type=resource_type)
                )
            self.ProcessResult.objects.bulk_create(creates)
            self.ProcessResult.objects.bulk_update(updates, ["result_type", "result_id"])

    def merge_batch(self, batch):

        pipeline_phase = self.config.pipeline_phase
        config = create_config("extract_processor", self.config.contribute_data)
        contribution_processor = config.extractor
        contribution_property = config.to_property

        while True:

            documents = []
            for process_result in batch.processresult_set.filter(result_id__isnull=False):
                result = process_result.result
                # Write results to the pipeline
                process_result.document.pipeline[pipeline_phase] = {
                    "success": result.success,
                    "resource": f"{result._meta.app_label}.{result._meta.model_name}",
                    "id": result.id
                }
                documents.append(process_result.document)
                # Write data to the Document
                extractor_name, method_name = Processor.get_processor_components(contribution_processor)
                extractor_class = Processor.get_processor_class(extractor_name)
                extractor = extractor_class(config)
                extractor_method = getattr(extractor, method_name)
                contributions = list(extractor_method(result))
                if not len(contributions):
                    continue
                contribution = contributions.pop(0)
                # TODO: create docs here where necessary
                if contribution_property is None:
                    process_result.document.properties.update(contribution)
                else:
                    process_result.document.properties[contribution_property] = contribution

            # We'll be locking the Documents for update to prevent accidental overwrite of parallel results
            with transaction.atomic():
                try:
                    list(self.Document.objects.filter(id__in=[doc.id for doc in documents]).select_for_update())
                except transaction.DatabaseError:
                    continue
                self.Document.objects.bulk_update(documents, ["pipeline", "properties"])
                break
