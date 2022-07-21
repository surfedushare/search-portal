import logging
from copy import copy

from django.conf import settings


harvester = logging.getLogger('harvester')
documents = logging.getLogger('documents')
results = logging.getLogger('results')


class HarvestLogger(object):

    dataset = None
    command = None
    command_options = None

    def __init__(self, dataset, command, command_options):
        self.dataset = dataset
        self.command = command
        self.command_options = command_options

    def _get_extra_info(self, phase=None, progress=None, material=None, result=None):
        return {
            "dataset": self.dataset,
            "command": self.command,
            "command_options": self.command_options,
            "version": settings.VERSION,
            "commit": settings.GIT_COMMIT,
            "phase": phase,
            "progress": progress,
            "material": material,
            "result": result or {}
        }

    def debug(self, message):
        extra = self._get_extra_info()
        harvester.debug(message, extra=extra)

    def info(self, message):
        extra = self._get_extra_info()
        harvester.info(message, extra=extra)

    def warning(self, message):
        extra = self._get_extra_info()
        harvester.warning(message, extra=extra)

    def error(self, message):
        extra = self._get_extra_info()
        harvester.error(message, extra=extra)

    def start(self, phase):
        extra = self._get_extra_info(phase=phase, progress="start")
        harvester.info(f"Starting: {phase}", extra=extra)

    def progress(self, phase, total, success=None, fail=None):
        extra = self._get_extra_info(phase=phase, progress="busy", result={
            "success": success,
            "fail": fail,
            "total": total
        })
        harvester.debug(f"Progress: {phase}", extra=extra)

    def end(self, phase, success=None, fail=None):
        extra = self._get_extra_info(phase=phase, progress="end", result={
            "success": success,
            "fail": fail,
            "total": None
        })
        harvester.info(f"Ending: {phase}", extra=extra)

    def report_material(self, external_id, title=None, url=None, pipeline=None, state="upsert", copyright=None,
                        lowest_educational_level=None):
        material_info = {
            "external_id": external_id,
            "title": title,
            "url": url
        }
        if state == "inactive":
            material_info.update({
                "copyright": copyright,
                "lowest_educational_level": lowest_educational_level
            })
        pipeline = pipeline or {}
        # Report on pipeline steps
        for step, result in pipeline.items():
            if step == "harvest":  # skips harvest metadata (commit)
                continue
            if result["resource"] is None:  # do not report non-existent pipeline steps
                continue
            if state == "preview" and step != "preview":  # prevents double reporting
                continue
            material = copy(material_info)
            material.update({
                "step": step,
                "success": result["success"],
                "resource": result["resource"][0],
                "resource_id": result["resource"][1],
            })
            if result["success"]:
                extra = self._get_extra_info(phase="report", material=material)
                documents.info(f"Pipeline success: {external_id}", extra=extra)
            else:
                extra = self._get_extra_info(phase="report", material=material)
                documents.error(f"Pipeline error: {external_id}", extra=extra)
        # Report material state
        material_info.update({
            "step": state
        })
        extra = self._get_extra_info(phase="report", material=material_info)
        documents.info(f"Report: {external_id}", extra=extra)

    def _get_document_counts(self, document_set):
        total = document_set.count()
        inactive_educational_level_count = document_set \
            .filter(properties__state="inactive", properties__lowest_educational_level__lte=1) \
            .count()
        inactive_copyright_count = \
            document_set.filter(properties__state="inactive").count() - inactive_educational_level_count
        return {
            "total": total - inactive_educational_level_count - inactive_copyright_count,
            "inactive_educational_level_count": inactive_educational_level_count,
            "inactive_copyright_count": inactive_copyright_count
        }

    def report_collection(self, collection, repository):
        document_counts = self._get_document_counts(collection.document_set)
        extra = self._get_extra_info(result={
            "source": collection.name,
            "repository": repository,
            "total": document_counts["total"],
            "inactive": {
                "educational_level": document_counts["inactive_educational_level_count"],
                "copyright": document_counts["inactive_copyright_count"]
            }
        })
        results.info(f"{collection.name} ({repository}) => {document_counts['total']}", extra=extra)

    def report_dataset_version(self, dataset_version):
        collection_names = set()
        collection_ids = set()
        for collection in dataset_version.collection_set.all():
            if collection.name in collection_names:
                continue
            collection_names.add(collection.name)
            collection_ids.add(collection.id)
            self.report_collection(collection, None)
        document_counts = self._get_document_counts(
            dataset_version.document_set.filter(collection__id__in=collection_ids)
        )
        extra = self._get_extra_info(result={
            "source": str(dataset_version),
            "repository": None,
            "total": document_counts["total"],
            "inactive": {
                "educational_level": document_counts["inactive_educational_level_count"],
                "copyright": document_counts["inactive_copyright_count"]
            }
        })
        results.info(f"{dataset_version} => {document_counts['total']}", extra=extra)

    def elastic_errors(self, errors):
        for error in errors:
            if "index" in error:
                self.error(f"Unable to index {error['index']['_id']}: {error['index']['error']}")
            elif "delete" in error and error["delete"]["result"] == "not_found":
                self.warning(f"Unable to delete document that does not exist: {error['delete']['_id']}")
            else:
                self.error(f"Unknown elastic error: {error}")
