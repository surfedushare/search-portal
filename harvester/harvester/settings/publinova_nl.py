from harvester.settings.base import *
from search_client import DocumentTypes


DOCUMENT_TYPE = DocumentTypes.RESEARCH_PRODUCT
ALLOW_CLOSED_ACCESS_DOCUMENTS = environment.service.env != "production"
LOWEST_EDUCATIONAL_LEVEL = -1  # will ignore lowest educational level requirements
