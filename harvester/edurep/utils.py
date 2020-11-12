import logging
from urlobject import URLObject

from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor

from edurep.models import EdurepOAIPMH
from edurep.extraction import EdurepDataExtraction


EDUREP_EXTRACTION_OBJECTIVE = {
    "url": EdurepDataExtraction.get_url,
    "files": EdurepDataExtraction.get_files,
    "title": EdurepDataExtraction.get_title,
    "language": EdurepDataExtraction.get_language,
    "keywords": EdurepDataExtraction.get_keywords,
    "description": EdurepDataExtraction.get_description,
    "mime_type": EdurepDataExtraction.get_mime_type,
    "copyright": EdurepDataExtraction.get_copyright,
    "aggregation_level": EdurepDataExtraction.get_aggregation_level,
    "author": EdurepDataExtraction.get_author,
    "authors": EdurepDataExtraction.get_authors,
    "publishers": EdurepDataExtraction.get_publishers,
    "publisher_date": EdurepDataExtraction.get_publisher_date,
    "lom_educational_levels": EdurepDataExtraction.get_lom_educational_levels,
    "educational_levels": EdurepDataExtraction.get_educational_levels,
    "humanized_educational_levels": EdurepDataExtraction.get_humanized_educational_levels,
    "lowest_educational_level": EdurepDataExtraction.get_lowest_educational_level,
    "disciplines": EdurepDataExtraction.get_disciplines,
    "humanized_disciplines": EdurepDataExtraction.get_humanized_disciplines,
}


err = logging.getLogger(__file__)


def get_edurep_oaipmh_seeds(set_specification, latest_update, include_deleted=True):
    queryset = EdurepOAIPMH.objects\
        .filter(set_specification=set_specification, since__date__gte=latest_update.date(), status=200)

    oaipmh_objective = {
        "@": EdurepDataExtraction.get_oaipmh_records,
        "external_id": EdurepDataExtraction.get_oaipmh_external_id,
        "state": EdurepDataExtraction.get_oaipmh_record_state
    }
    oaipmh_objective.update(EDUREP_EXTRACTION_OBJECTIVE)
    extract_config = create_config("extract_processor", {
        "objective": oaipmh_objective
    })
    prc = ExtractProcessor(config=extract_config)

    results = []
    for harvest in queryset:
        try:
            results += list(prc.extract_from_resource(harvest))
        except ValueError as exc:
            err.warning("Invalid XML:", exc, harvest.uri)
    seeds = []
    for seed in results:
        # Some records in Edurep do not have any known URL
        # As we can't possibly process those we ignore them (silently)
        # If we want to fix this it should happen on Edurep's or Sharekit's side
        # We informed Kirsten van Veelo and Martine Teirlinck about the situation.
        if seed["state"] == "active" and not seed["url"]:
            continue
        # We adjust url's of seeds if the source files are not at the URL
        # We should improve data extraction to always get source files
        url = seed.get("url", None)
        if url and "maken.wikiwijs.nl" in url:
            package_url = URLObject(seed["url"])
            seed["package_url"] = package_url.with_fragment("").with_query("p=imscp")
        # We deduplicate based on the external_id a UID by Edurep
        seeds.append(seed)
    # Now we'll mark any invalid seeds as deleted to make sure they disappear
    # Invalid seeds have a copyright or are of insufficient education level
    for seed in seeds:
        if not seed["copyright"] or seed["copyright"] == "no":
            seed["state"] = "deleted"
        if seed["lowest_educational_level"] < 1:  # lower level than MBO
            seed["state"] = "deleted"
    # And we return the seeds based on whether to include deleted or not
    return seeds if include_deleted else \
        [result for result in seeds if result.get("state", "active") == "active"]
