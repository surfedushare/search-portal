class Repositories:
    EDUREP = "edurep.EdurepOAIPMH"
    SHAREKIT = "sharekit.SharekitMetadataHarvest"
    ANATOMY_TOOL = "anatomy_tool.AnatomyToolOAIPMH"
    HANZE = "hanze.HanzeResearchObjectResource"


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


HIGHER_EDUCATION_LEVELS = {  # TODO: consider whether to strip this down to strict LOM without add-ons
    "Volwasseneneducatie": 1,
    "Praktijkonderwijs": 1,
    "Beroepsonderwijs en Volwasseneneducatie": 1,
    "Middenkaderopleiding": 1,
    "MBO": 1,
    "HBO": 2,
    "WO": 3
}


RESTRICTED_MATERIAL_SETS = {
    "l4l",
    "surfsharekit_restricted",
    "edusourcesprivate"
}
