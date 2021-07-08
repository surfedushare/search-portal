from django.contrib.contenttypes.models import ContentType

from datagrowth.configuration import create_config
from datagrowth.resources.http.tasks import send

from core.processors.pipeline.base import PipelineProcessor


class HttpPipelineProcessor(PipelineProcessor):

    def process_batch(self, batch):

        config = create_config("http_resource", self.config.resource_process)
        app_label, resource_model = config.resource.split(".")
        resource_type = ContentType.objects.get_by_natural_key(app_label, resource_model)

        updates = []
        creates = []
        for process_result in batch.processresult_set.all():
            args, kwargs = process_result.document.output(config.args, config.kwargs)
            successes, fails = send(*args, **kwargs, config=config, method=config.method)
            results = successes + fails
            if not len(results):
                continue
            result_id = results.pop(0)
            process_result.result_type = resource_type
            process_result.result_id = result_id
            updates.append(process_result)
            for result_id in results:
                creates.append(
                    self.ProcessResult(document=process_result.document, batch=batch,
                                       result_id=result_id, result_type=resource_type)
                )
            self.ProcessResult.objects.bulk_create(creates)
            self.ProcessResult.objects.bulk_update(updates, ["result_type", "result_id"])

    def merge_batch(self, batch):

        config = create_config("http_resource", self.config.resource_process)
        result_key = config.result_key

        documents = []
        for process_result in batch.processresult_set.filter(result_id__isnull=False):
            result = process_result.result
            process_result.document.pipeline[result_key] = {
                "success": result.success,
                "resource": f"{result._meta.app_label}.{result._meta.model_name}",
                "id": result.id
            }
            documents.append(process_result.document)
        self.Document.objects.bulk_update(documents, ["pipeline"])

    def full_merge(self, queryset):
        self.ProcessResult.objects.filter(document__in=queryset).delete()
