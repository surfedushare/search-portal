from .base import *

SITE_ID = 2
SITE_SLUG = "mbo"

OPENSEARCH_NL_INDEX = "mbo-nl"
OPENSEARCH_EN_INDEX = "mbo-en"
OPENSEARCH_UNK_INDEX = "mbo-unk"

SITE_PREFERRED_FILTERS = [
    {
        "external_id": "lom_educational_levels",
        "items": ["BVE"]
    }
]
