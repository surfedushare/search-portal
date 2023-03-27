class Repositories:
    EDUREP_JSONSEARCH = "sources.EdurepJsonSearchResource"
    EDUREP = "edurep.EdurepOAIPMH"
    SHAREKIT = "sharekit.SharekitMetadataHarvest"
    ANATOMY_TOOL = "anatomy_tool.AnatomyToolOAIPMH"
    HANZE = "sources.HanzeResearchObjectResource"
    HAN = "sources.HanOAIPMHResource"
    HVA = "sources.HvaPureResource"
    HKU = "sources.HkuMetadataResource"
    GREENI = "sources.GreeniOAIPMHResource"
    BUAS = "sources.BuasPureResource"


def get_repository_id(repository_resource):
    repository_id = next(
        (choice[1] for choice in REPOSITORY_CHOICES if choice[0] == repository_resource),
        None
    )
    if repository_id is None:
        return
    return repository_id.lower()


REPOSITORY_CHOICES = [
    (value, attr.lower().capitalize())
    for attr, value in sorted(Repositories.__dict__.items()) if not attr.startswith("_")
]


class DeletePolicies:
    """
    Details: http://www.openarchives.org/OAI/openarchivesprotocol.html#DeletedRecords
    """
    NO = "no"
    PERSISTENT = "persistent"
    TRANSIENT = "transient"


DELETE_POLICY_CHOICES = [
    (value, attr.lower().capitalize())
    for attr, value in sorted(DeletePolicies.__dict__.items()) if not attr.startswith("_")
]


class HarvestStages:
    NEW = "New"
    BASIC = "Basic"
    VIDEO = "Video"
    PREVIEW = "Preview"
    COMPLETE = "Complete"


HARVEST_STAGE_CHOICES = [
    (value, value) for attr, value in sorted(HarvestStages.__dict__.items()) if not attr.startswith("_")
]


PLAIN_TEXT_MIME_TYPES = [
    "text/html",
    "application/msword",
    "application/octet-stream",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/xhtml+xml",
    "application/vnd.ms-powerpoint",
]


HIGHER_EDUCATION_LEVELS = {
    "BVE": 1,
    "HBO": 2,
    "HBO - Bachelor": 2,
    "HBO - Master": 2,
    "WO": 3,
    "WO - Bachelor": 3,
    "WO - Master": 3,
}


MINIMAL_EDUCATIONAL_LEVEL_BY_DOMAIN = {
    "harvester.prod.surfedushare.nl": 2,
    "harvester.mbo.prod.surfedushare.nl": 1,
    "harvester.publinova.nl": None,
}

SITE_SHORTHAND_BY_DOMAIN = {
    "harvester.prod.surfedushare.nl": "edusources",
    "harvester.mbo.prod.surfedushare.nl": "mbo",
    "harvester.publinova.nl": "publinova",
}

EXCLUDED_COLLECTIONS_BY_DOMAIN = {
    "harvester.prod.surfedushare.nl": ["edusourcesmbo", "edusourcesmboprivate"],
    "harvester.mbo.prod.surfedushare.nl": [],
    "harvester.publinova.nl": [],
}
