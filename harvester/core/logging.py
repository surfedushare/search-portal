import logging


logger = logging.getLogger('harvester')


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
        logger.debug(message, extra=extra)

    def info(self, message):
        extra = self._get_extra_info(level="INFO")
        logger.info(message, extra=extra)

    def warning(self, message):
        extra = self._get_extra_info(level="WARNING")
        logger.warning(message, extra=extra)

    def error(self, message):
        extra = self._get_extra_info(level="ERROR")
        logger.error(message, extra=extra)

    def start(self, phase):
        extra = self._get_extra_info(level="INFO", phase=phase, progress="start")
        logger.info(f"Starting: {phase}", extra=extra)

    def progress(self, phase, current, total, success=None, fail=None):
        extra = self._get_extra_info(level="DEBUG", phase=phase, progress="busy", result={
            "success": success,
            "fail": fail,
            "current": current,
            "total": total
        })
        logger.debug(f"Progress: {phase}", extra=extra)

    def end(self, phase, success=None, fail=None):
        extra = self._get_extra_info(level="INFO", phase=phase, progress="end", result={
            "success": success,
            "fail": fail,
            "current": None,
            "total": None
        })
        logger.info(f"Ending: {phase}", extra=extra)

    def report_material(self, external_id, title, url, pipeline):
        extra = self._get_extra_info(level="DEBUG", phase="report", material={
            "external_id": external_id,
            "title": title,
            "url": url,
            "pipeline": pipeline
        })
        logger.debug(f"Report: {external_id}", extra=extra)
