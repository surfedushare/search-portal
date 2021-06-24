import re
from mimetypes import guess_type

from django.conf import settings

from datagrowth.utils import reach

from core.constants import HIGHER_EDUCATION_LEVELS, RESTRICTED_MATERIAL_SETS


class SharekitMetadataExtraction(object):

    youtube_regex = re.compile(r".*(youtube\.com|youtu\.be).*", re.IGNORECASE)

    @classmethod
    def get_record_state(cls, node):
        return "active"

    #############################
    # GENERIC
    #############################

    @classmethod
    def get_files(cls, node):
        files = node["attributes"]["files"] or []
        links = node["attributes"]["links"] or []
        output = [
            [file["resourceMimeType"], file["url"], file["fileName"]]
            for file in files if file["resourceMimeType"] and file["url"]
        ]
        output += [
            ["text/html", link["url"], f"URL {ix+1}"]
            for ix, link in enumerate(links)
        ]
        return output

    @classmethod
    def get_url(cls, node):
        files = cls.get_files(node)
        if not files:
            return
        url = files[0][1]
        return url.strip()

    @classmethod
    def get_mime_type(cls, node):
        files = cls.get_files(node)
        if not files:
            return
        return files[0][0]

    @classmethod
    def get_technical_type(cls, node):
        technical_type = node["attributes"]["technicalFormat"]
        if technical_type:
            return technical_type
        files = cls.get_files(node)
        if not files:
            return "unknown"
        technical_type = settings.MIME_TYPE_TO_TECHNICAL_TYPE.get(files[0][0], None)
        if technical_type:
            return technical_type
        file_url = files[0][1]
        if not file_url:
            return "unknown"
        mime_type, encoding = guess_type(file_url)
        return settings.MIME_TYPE_TO_TECHNICAL_TYPE.get(mime_type, "unknown")

    @classmethod
    def get_material_type(cls, node):
        material_type = node["attributes"]["typeLearningMaterial"]
        return [material_type] if material_type else []

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
        publishers = []
        publisher = node["attributes"]["publishers"]
        keywords = node["attributes"]["keywords"] or []
        # Check HBOVPK tags
        hbovpk_keywords = [keyword for keyword in keywords if keyword and "hbovpk" in keyword.lower()]
        if hbovpk_keywords:
            publishers.append("HBO Verpleegkunde")
        # Check normal publishers
        if not publisher:
            return publishers
        publishers.append(publisher)
        return publishers

    @classmethod
    def get_lom_educational_levels(cls, node):
        educational_levels = node["attributes"]["educationalLevels"]
        if not educational_levels:
            return []
        return list(set([
            educational_level["value"] for educational_level in educational_levels
            if educational_level["value"]
        ]))

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
    def get_disciplines(cls, node):
        return []

    @classmethod
    def get_ideas(cls, node):
        compound_ideas = [vocabulary["value"] for vocabulary in node["attributes"]["vocabularies"]]
        if not compound_ideas:
            return []
        ideas = []
        for compound_idea in compound_ideas:
            ideas += compound_idea.split(" - ")
        return list(set(ideas))

    @classmethod
    def get_is_restricted(cls, data):
        link = data["links"]["self"]
        for restricted_set in RESTRICTED_MATERIAL_SETS:
            if restricted_set in link:
                return True
        return False

    @classmethod
    def get_analysis_allowed(cls, node):
        # We disallow analysis for non-derivative materials as we'll create derivatives in that process
        # NB: any material that is_restricted will also have analysis_allowed set to False
        copyright = SharekitMetadataExtraction.get_copyright(node)
        return (copyright is not None and "nd" not in copyright) and copyright != "yes"

    @classmethod
    def get_is_part_of(cls, node):
        return reach("$.attributes.partOf", node)


SHAREKIT_EXTRACTION_OBJECTIVE = {
    "url": SharekitMetadataExtraction.get_url,
    "files": SharekitMetadataExtraction.get_files,
    "title": "$.attributes.title",
    "language": "$.attributes.language",
    "keywords": "$.attributes.keywords",
    "description": "$.attributes.abstract",
    "mime_type": SharekitMetadataExtraction.get_mime_type,
    "technical_type": SharekitMetadataExtraction.get_technical_type,
    "material_type": SharekitMetadataExtraction.get_material_type,
    "copyright": SharekitMetadataExtraction.get_copyright,
    "copyright_description": lambda node: None,
    "aggregation_level": "$.attributes.aggregationlevel",
    "authors": SharekitMetadataExtraction.get_authors,
    "publishers": SharekitMetadataExtraction.get_publishers,
    "publisher_date": "$.attributes.publishedAt",
    "lom_educational_levels": SharekitMetadataExtraction.get_lom_educational_levels,
    "lowest_educational_level": SharekitMetadataExtraction.get_lowest_educational_level,
    "disciplines": SharekitMetadataExtraction.get_disciplines,
    "ideas": SharekitMetadataExtraction.get_ideas,
    "from_youtube": SharekitMetadataExtraction.get_from_youtube,
    "#is_restricted": SharekitMetadataExtraction.get_is_restricted,
    "analysis_allowed": SharekitMetadataExtraction.get_analysis_allowed,
    "is_part_of": SharekitMetadataExtraction.get_is_part_of,
    "has_parts": "$.attributes.hasParts",
    "doi": "$.attributes.doi",
}
