import logging
from copy import copy


harvester = logging.getLogger('harvester')
documents = logging.getLogger('documents')


class HarvestLogger(object):

    dataset = None
    command = None
    command_options = None

    def __init__(self, dataset, command, command_options):
        self.dataset = dataset
        self.command = command
        self.command_options = command_options

    def _get_extra_info(self, level, phase=None, progress=None, material=None, result=None):
        return {
            "dataset": self.dataset,
            "command": self.command,
            "command_options": self.command_options,
            "level": level,
            "phase": phase,
            "progress": progress,
            "material": material,
            "result": result
        }

    def debug(self, message):
        extra = self._get_extra_info(level="DEBUG")
        harvester.debug(message, extra=extra)

    def info(self, message):
        extra = self._get_extra_info(level="INFO")
        harvester.info(message, extra=extra)

    def warning(self, message):
        extra = self._get_extra_info(level="WARNING")
        harvester.warning(message, extra=extra)

    def error(self, message):
        extra = self._get_extra_info(level="ERROR")
        harvester.error(message, extra=extra)

    def start(self, phase):
        extra = self._get_extra_info(level="INFO", phase=phase, progress="start")
        harvester.info(f"Starting: {phase}", extra=extra)

    def progress(self, phase, total, success=None, fail=None):
        extra = self._get_extra_info(level="DEBUG", phase=phase, progress="busy", result={
            "success": success,
            "fail": fail,
            "total": total
        })
        harvester.debug(f"Progress: {phase}", extra=extra)

    def end(self, phase, success=None, fail=None):
        extra = self._get_extra_info(level="INFO", phase=phase, progress="end", result={
            "success": success,
            "fail": fail,
            "total": None
        })
        harvester.info(f"Ending: {phase}", extra=extra)

    def report_material(self, external_id, title=None, url=None, pipeline=None, state="upsert"):
        material_info = {
            "external_id": external_id,
            "title": title,
            "url": url
        }
        pipeline = pipeline or {}
        # Report on pipeline steps
        for step, result in pipeline.items():
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
                extra = self._get_extra_info(level="INFO", phase="report", material=material)
                documents.info(f"Pipeline success: {external_id}", extra=extra)
            else:
                extra = self._get_extra_info(level="ERROR", phase="report", material=material)
                documents.error(f"Pipeline error: {external_id}", extra=extra)
        # Report material state
        material_info.update({
            "state": state
        })
        extra = self._get_extra_info(level="INFO", phase="report", material=material_info)
        documents.info(f"Report: {external_id}", extra=extra)
