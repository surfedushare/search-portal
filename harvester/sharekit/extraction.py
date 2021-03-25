import re

from datagrowth.utils import reach

from core.constants import HIGHER_EDUCATION_LEVELS, RESTRICTED_MATERIAL_OAIPMH_SETS


class SharekitMetadataExtraction(object):

    youtube_regex = re.compile(r".*(youtube\.com|youtu\.be).*", re.IGNORECASE)

    @classmethod
    def get_record_state(cls, node):
        return "active"

    #############################
    # GENERIC
    #############################

    @classmethod
    def get_files(cls, soup, el):
        mime_types = el.find_all('czp:format')
        urls = el.find_all('czp:location')
        return list(
            zip(
                [mime_node.text.strip() for mime_node in mime_types],
                [url_node.text.strip() for url_node in urls],
            )
        )

    @classmethod
    def get_url(cls, node):
        return reach("$.attributes.file.0.url", node)

    @classmethod
    def get_copyright(cls, node):
        return node["attributes"]["termsOfUse"]

    @classmethod
    def get_from_youtube(cls, node):
        url = cls.get_url(node)
        if not url:
            return False
        return cls.youtube_regex.match(url) is not None

    @classmethod
    def get_authors(cls, node):
        return [
            author["person"]["name"]
            for author in node["attributes"]["authors"]
        ]

    @classmethod
    def get_publishers(cls, node):
        publisher = node["attributes"]["publisher"]
        if not publisher:
            return []
        return [publisher]

    @classmethod
    def get_lom_educational_levels(cls, node):
        educational_level = node["attributes"]["publisher"]
        if not educational_level:
            return []
        return [educational_level]

    @classmethod
    def get_lowest_educational_level(cls, node):
        educational_levels = cls.get_lom_educational_levels(node)
        current_numeric_level = 3 if len(educational_levels) else -1
        for education_level in educational_levels:
            for higher_education_level, numeric_level in HIGHER_EDUCATION_LEVELS.items():
                if not education_level.startswith(higher_education_level):
                    continue
                # One of the records education levels matches a higher education level.
                # We re-assign current level and stop processing this education level,
                # as it shouldn't match multiple higher education levels
                current_numeric_level = min(current_numeric_level, numeric_level)
                break
            else:
                # No higher education level found inside current education level.
                # Dealing with an "other" means a lower education level than we're interested in.
                # So this record has the lowest possible level. We're done processing this seed.
                current_numeric_level = 0
                break
        return current_numeric_level

    @classmethod
    def get_ideas(cls, node):
        ideas = node["attributes"]["vocabulary"]
        if not ideas:
            return []
        return ideas.split(" - ")

    @classmethod
    def get_analysis_allowed(cls, node):
        # We don't have access to restricted materials so we disallow analysis for them
        external_id = node["id"]
        for restricted_set in RESTRICTED_MATERIAL_OAIPMH_SETS:
            if external_id.startswith(restricted_set + ":"):
                return False
        # We also disallow analysis for non-derivative materials as we'll create derivatives in that process
        copyright = SharekitMetadataExtraction.get_copyright(node)
        return (copyright is not None and "nd" not in copyright) and copyright != "yes"

    @classmethod
    def get_is_part_of(cls, node):
        return reach("$.attributes.partOf.0", node)


SHAREKIT_EXTRACTION_OBJECTIVE = {
    "url": SharekitMetadataExtraction.get_url,  # TODO: more selection??
    # "files": EdurepDataExtraction.get_files,  # TODO: add this
    "title": "$.attributes.title",
    "language": "$.attributes.language",
    "keywords": "$.attributes.keywords",
    "description": "$.attributes.abstract",
    "mime_type": "text/html",  # TODO: add this
    "copyright": SharekitMetadataExtraction.get_copyright,
    "aggregation_level": "$.attributes.aggregationlevel",
    "authors": SharekitMetadataExtraction.get_authors,
    "publishers": SharekitMetadataExtraction.get_publishers,  # TODO: only one?
    "publisher_date": "$.attributes.dateIssued",
    "lom_educational_levels": SharekitMetadataExtraction.get_lom_educational_levels,  # TODO: only one?
    "lowest_educational_level": SharekitMetadataExtraction.get_lowest_educational_level,
    "disciplines": [],  # TODO: add this
    "ideas": SharekitMetadataExtraction.get_ideas,
    "from_youtube": SharekitMetadataExtraction.get_from_youtube,
    "analysis_allowed": SharekitMetadataExtraction.get_analysis_allowed,
    "is_part_of": SharekitMetadataExtraction.get_is_part_of,  # TODO: multiple?
    "has_part": "$.attributes.hasParts"
}
