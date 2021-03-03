import logging
from urlobject import URLObject

from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor

from edurep.models import EdurepOAIPMH
from edurep.extraction import EdurepDataExtraction


logger = logging.getLogger("harvester")


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
    "ideas": EdurepDataExtraction.get_ideas,
    "from_youtube": EdurepDataExtraction.get_from_youtube,
    "analysis_allowed": EdurepDataExtraction.get_analysis_allowed,
    "is_part_of": EdurepDataExtraction.get_is_part_of,
    "has_part": EdurepDataExtraction.get_has_part,
}


def get_edurep_oaipmh_seeds(set_specification, latest_update, include_deleted=True, include_no_url=False):
    """
    Extracts metadata from OAI-PMH XML responses by Edurep.
    More information on Edurep: https://developers.wiki.kennisnet.nl/index.php/Edurep:Hoofdpagina
    """
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
            logger.warning("Invalid XML:", exc, harvest.uri)
    seeds = []
    for seed in results:
        # In many cases it doesn't make sense to try and process files without a URL
        # So by default we skip these seeds,
        # but some seeds that group together materials do not have files/URLs and you can include these
        if seed["state"] == "active" and not seed["url"] and not include_no_url:
            continue
        url = seed.get("url", None)  # None for some parent materials
        # When dealing with Wikiwijs Maken we also get packages instead of just the plain HTML
        if url and "maken.wikiwijs.nl" in url:
            package_url = URLObject(seed["url"])
            seed["package_url"] = package_url.with_fragment("").with_query("p=imscp")
        # We deduplicate based on the external_id a UID by Edurep
        seeds.append(seed)
    # Now we'll mark any invalid seeds as deleted to make sure they disappear
    # Invalid seeds have a copyright or are of insufficient education level
    for seed in seeds:
        if not seed["copyright"]:  # tmp disable of all-rights-reserved (or seed["copyright"] == "yes":)
            seed["state"] = "deleted"
        if seed["lowest_educational_level"] < 1:  # lower level than MBO
            seed["state"] = "deleted"
    # And we return the seeds based on whether to include deleted or not
    return seeds if include_deleted else \
        [result for result in seeds if result.get("state", "active") == "active"]
