import django_log_formatter_json
import logging


logger = logging.getLogger('harvester')


def _convert_to_extra_field(level=None, **kwargs):
    extra = kwargs
    extra['level'] = level
    return extra


def debug(message, **kwargs):
    extra = _convert_to_extra_field(level='DEBUG', **kwargs)
    logger.debug(message, extra=extra)


def info(message, **kwargs):
    extra = _convert_to_extra_field(level='INFO', **kwargs)
    logger.info(message, extra=extra)
