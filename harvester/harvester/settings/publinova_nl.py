from harvester.settings.base import *
from search_client import DocumentTypes


DOCUMENT_TYPE = DocumentTypes.RESEARCH_PRODUCT
ALLOW_CLOSED_ACCESS_DOCUMENTS = False
LOWEST_EDUCATIONAL_LEVEL = -1  # will ignore lowest educational level requirements

CELERY_TASK_DEFAULT_QUEUE = "publinova"
CELERY_TASK_ROUTES = {
    'sync_indices': {'queue': 'publinova-indexing'}
}
