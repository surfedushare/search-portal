import re

from datagrowth.utils import reach

from core.constants import HIGHER_EDUCATION_LEVELS, RESTRICTED_MATERIAL_OAIPMH_SETS


class SharekitMetadataExtraction(object):

    youtube_regex = re.compile(r".*(youtube\.com|youtu\.be).*", re.IGNORECASE)

    @classmethod
    def get_record_state(cls, node):
        return "active"

    @classmethod
    def mirror(cls, value):
        return lambda node: value

    #############################
    # GENERIC
    #############################

    @classmethod
    def get_files(cls, node):
        files = node["attributes"]["file"] or []
        links = node["attributes"]["link"] or []
        output = [
            [file["resourceMimeType"], file["url"]]
            for file in files
        ]
        output += [
            ["text/html", link["url"]]
            for link in links
        ]
        return output

    @classmethod
    def get_url(cls, node):
        files = cls.get_files(node)
        if not files:
            return
        return files[0][1]

    @classmethod
    def get_mime_type(cls, node):
        files = cls.get_files(node)
        if not files:
            return
        return files[0][0]

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
        authors = node["attributes"]["authors"] or []
        return [
            author["person"]["name"]
            for author in authors
        ]

    @classmethod
    def get_publishers(cls, node):
        publisher = node["attributes"]["publisher"]
        if not publisher:
            return []
        return [publisher]

    @classmethod
    def get_lom_educational_levels(cls, node):
        educational_level = node["attributes"]["level"]
        if not educational_level:
            return []
        return [educational_level] if isinstance(educational_level, str) else educational_level

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
        compound_ideas = reach("$.0.taxonPath.0.taxon.entry", node)
        if not compound_ideas:
            return []
        ideas = []
        for compound_idea in compound_ideas:
            ideas += compound_idea.split(" - ")
        return list(set(ideas))

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
    "url": SharekitMetadataExtraction.get_url,  # REFACTOR: more selection??
    "files": SharekitMetadataExtraction.get_files,
    "title": "$.attributes.title",
    "language": "$.attributes.language",
    "keywords": "$.attributes.keywords",
    "description": "$.attributes.abstract",
    "mime_type": SharekitMetadataExtraction.get_mime_type,
    "copyright": SharekitMetadataExtraction.get_copyright,
    "aggregation_level": "$.attributes.aggregationlevel",
    "authors": SharekitMetadataExtraction.get_authors,
    "publishers": SharekitMetadataExtraction.get_publishers,  # REFACTOR: only one?
    "publisher_date": "$.attributes.dateIssued",
    "lom_educational_levels": SharekitMetadataExtraction.get_lom_educational_levels,  # REFACTOR: only one?
    "lowest_educational_level": SharekitMetadataExtraction.get_lowest_educational_level,
    "disciplines": SharekitMetadataExtraction.mirror([]),  # REFACTOR: add this
    "ideas": SharekitMetadataExtraction.get_ideas,  # REFACTOR: simplify?
    "from_youtube": SharekitMetadataExtraction.get_from_youtube,
    "analysis_allowed": SharekitMetadataExtraction.get_analysis_allowed,
    "is_part_of": SharekitMetadataExtraction.get_is_part_of,  # REFACTOR: multiple?
    "has_parts": "$.attributes.hasParts"
}
