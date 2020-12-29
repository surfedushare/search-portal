import logging

logger = logging.getLogger('harvester')


def _convert_to_extra_field(level=None, **kwargs):
    extra = kwargs
    extra['level'] = level
    return extra


def debug(message, *args, **kwargs):
    extra = _convert_to_extra_field(level='DEBUG', **kwargs)
    logger.debug(message, *args, extra=extra)


def info(message, *args, **kwargs):
    extra = _convert_to_extra_field(level='INFO', **kwargs)
    logger.info(message, *args, extra=extra)


def warning(message, *args, **kwargs):
    extra = _convert_to_extra_field(level='WARNING', **kwargs)
    logger.warning(message, *args, extra=extra)
