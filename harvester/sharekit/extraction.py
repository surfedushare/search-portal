import re
from mimetypes import guess_type
from hashlib import sha1
from dateutil.parser import parse as date_parser
from itertools import chain

from django.conf import settings

from datagrowth.processors import ExtractProcessor
from datagrowth.utils import reach

from core.constants import HIGHER_EDUCATION_LEVELS


class SharekitMetadataExtraction(ExtractProcessor):

    youtube_regex = re.compile(r".*(youtube\.com|youtu\.be).*", re.IGNORECASE)

    @classmethod
    def get_record_state(cls, node):
        return node.get("meta", {}).get("status", "active")

    #############################
    # GENERIC
    #############################

    @classmethod
    def parse_access_rights(cls, access_rights):
        if access_rights[0].isupper():  # value according to standard; no parsing necessary
            return access_rights
        access_rights = access_rights.replace("access", "")
        access_rights = access_rights.capitalize()
        access_rights += "Access"
        return access_rights

    @classmethod
    def get_files(cls, node):
        default_copyright = SharekitMetadataExtraction.get_copyright(node)
        files = node["attributes"].get("files", []) or []
        links = node["attributes"].get("links", []) or []
        output = [
            {
                "mime_type": file["resourceMimeType"],
                "url": file["url"],
                "hash": sha1(file["url"].encode("utf-8")).hexdigest(),
                "title": file["fileName"],
                "copyright": default_copyright,
                "access_rights": cls.parse_access_rights(file["accessRight"])
            }
            for file in files if file["resourceMimeType"] and file["url"]
        ]
        output += [
            {
                "mime_type": "text/html",
                "url": link["url"],
                "hash": sha1(link["url"].encode("utf-8")).hexdigest(),
                "title": link.get("urlName", None) or f"URL {ix+1}",
                "copyright": default_copyright,
                "access_rights": cls.parse_access_rights(link["accessRight"])
            }
            for ix, link in enumerate(links)
        ]
        return output

    @classmethod
    def get_url(cls, node):
        files = cls.get_files(node)
        if not files:
            return
        return files[0]["url"].strip()

    @classmethod
    def get_mime_type(cls, node):
        files = cls.get_files(node)
        if not files:
            return
        return files[0]["mime_type"]

    @classmethod
    def get_technical_type(cls, node):
        technical_type = node["attributes"].get("technicalFormat", None)
        if technical_type:
            return technical_type
        files = cls.get_files(node)
        if not files:
            return
        technical_type = settings.MIME_TYPE_TO_TECHNICAL_TYPE.get(files[0]["mime_type"], None)
        if technical_type:
            return technical_type
        file_url = files[0]["url"]
        if not file_url:
            return
        mime_type, encoding = guess_type(file_url)
        return settings.MIME_TYPE_TO_TECHNICAL_TYPE.get(mime_type, "unknown")

    @classmethod
    def get_material_types(cls, node):
        material_types = node["attributes"].get("typesLearningMaterial", [])
        if not material_types:
            return []
        elif isinstance(material_types, list):
            return [material_type for material_type in material_types if material_type]
        else:
            return [material_types]

    @classmethod
    def get_copyright(cls, node):
        return node["attributes"].get("termsOfUse", None)

    @classmethod
    def get_from_youtube(cls, node):
        url = cls.get_url(node)
        if not url:
            return False
        return cls.youtube_regex.match(url) is not None

    @classmethod
    def get_authors(cls, node):
        authors = node["attributes"].get("authors", []) or []
        return [
            {
                "name": author["person"]["name"],
                "email": author["person"]["email"],
                "external_id": author["person"]["id"],
                "dai": author["person"]["dai"],
                "orcid": author["person"]["orcid"],
                "isni": author["person"]["isni"],
            }
            for author in authors
        ]

    @classmethod
    def get_provider(cls, node):
        provider_name = None
        publishers = cls.get_publishers(node)
        if isinstance(publishers, str):
            provider_name = publishers
        if len(publishers):
            provider_name = publishers[0]
        return {
            "ror": None,
            "external_id": None,
            "slug": None,
            "name": provider_name
        }

    @classmethod
    def get_organizations(cls, node):
        root = cls.get_provider(node)
        root["type"] = "unknown"
        return {
            "root": root,
            "departments": [],
            "associates": []
        }

    @classmethod
    def get_consortium(cls, node):
        consortium = node["attributes"].get("consortium", None)
        if consortium is None:
            consortium_keywords = [
                keyword for keyword in node["attributes"].get("keywords", [])
                if "vaktherapie" in keyword.lower()
            ]
            if consortium_keywords:
                consortium = "Projectgroep Vaktherapie"
        return consortium

    @classmethod
    def get_publishers(cls, node):
        publishers = node["attributes"].get("publishers", []) or []
        if isinstance(publishers, str):
            publishers = [publishers]
        keywords = node["attributes"].get("keywords", []) or []
        # Check HBOVPK tags
        hbovpk_keywords = [keyword for keyword in keywords if keyword and "hbovpk" in keyword.lower()]
        if hbovpk_keywords:
            publishers.append("HBO Verpleegkunde")
        return publishers

    @classmethod
    def get_publisher_year(cls, node):
        publisher_date = node["attributes"].get("publishedAt", None)
        if not publisher_date:
            return
        publisher_datetime = date_parser(publisher_date)
        return publisher_datetime.year

    @classmethod
    def get_lom_educational_levels(cls, node):
        educational_levels = node["attributes"].get("educationalLevels", [])
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
    def get_ideas(cls, node):
        vocabularies = node["attributes"].get("vocabularies", {})
        terms = chain(*vocabularies.values())
        compound_ideas = [term["value"] for term in terms]
        if not compound_ideas:
            return []
        ideas = []
        for compound_idea in compound_ideas:
            ideas += compound_idea.split(" - ")
        return list(set(ideas))

    @classmethod
    def get_study_vocabulary(cls, node):
        vocabularies = node["attributes"].get("vocabularies", {})
        terms = chain(*vocabularies.values())
        return [term["source"] for term in terms]

    @classmethod
    def get_is_restricted(cls, node):
        return not cls.get_analysis_allowed(node)

    @classmethod
    def get_analysis_allowed(cls, node):
        files = cls.get_files(node)
        if not len(files):
            return False
        match files[0]["access_rights"], files[0]["copyright"]:
            case "OpenAccess", _:
                return True
            case "RestrictedAccess", copyright:
                return copyright and copyright not in ["yes", "unknown"] and "nd" not in copyright
            case "ClosedAccess", _:
                return False

    @classmethod
    def get_is_part_of(cls, node):
        return reach("$.attributes.partOf", node)

    @classmethod
    def get_research_themes(cls, node):
        theme_value = node["attributes"].get("themesResearchObject", [])
        if not theme_value:
            return []
        return theme_value if isinstance(theme_value, list) else [theme_value]

    @classmethod
    def get_empty_list(cls, node):
        return []

    @classmethod
    def get_none(cls, node):
        return None

    @classmethod
    def get_learning_material_disciplines(cls, node):
        discipline_value = node["attributes"].get("themesLearningMaterial", [])
        if not discipline_value:
            return []
        return discipline_value if isinstance(discipline_value, list) else [discipline_value]


SHAREKIT_EXTRACTION_OBJECTIVE = {
    "url": SharekitMetadataExtraction.get_url,
    "files": SharekitMetadataExtraction.get_files,
    "title": "$.attributes.title",
    "language": "$.attributes.language",
    "keywords": "$.attributes.keywords",
    "description": "$.attributes.abstract",
    "mime_type": SharekitMetadataExtraction.get_mime_type,
    "technical_type": SharekitMetadataExtraction.get_technical_type,
    "material_types": SharekitMetadataExtraction.get_material_types,
    "copyright": SharekitMetadataExtraction.get_copyright,
    "copyright_description": SharekitMetadataExtraction.get_none,
    "aggregation_level": "$.attributes.aggregationlevel",
    "authors": SharekitMetadataExtraction.get_authors,
    "provider": SharekitMetadataExtraction.get_provider,
    "organizations": SharekitMetadataExtraction.get_organizations,
    "publishers": SharekitMetadataExtraction.get_publishers,
    "publisher_date": "$.attributes.publishedAt",
    "publisher_year": SharekitMetadataExtraction.get_publisher_year,
    "lom_educational_levels": SharekitMetadataExtraction.get_lom_educational_levels,
    "lowest_educational_level": SharekitMetadataExtraction.get_lowest_educational_level,
    "studies": SharekitMetadataExtraction.get_empty_list,
    "ideas": SharekitMetadataExtraction.get_ideas,
    "study_vocabulary": SharekitMetadataExtraction.get_study_vocabulary,
    "from_youtube": SharekitMetadataExtraction.get_from_youtube,
    "is_restricted": SharekitMetadataExtraction.get_is_restricted,
    "analysis_allowed": SharekitMetadataExtraction.get_analysis_allowed,
    "is_part_of": SharekitMetadataExtraction.get_is_part_of,
    "has_parts": "$.attributes.hasParts",
    "doi": "$.attributes.doi",
    "research_object_type": "$.attributes.typeResearchObject",
    "research_themes": SharekitMetadataExtraction.get_research_themes,
    "parties": SharekitMetadataExtraction.get_empty_list,
    "learning_material_disciplines": SharekitMetadataExtraction.get_learning_material_disciplines,
    "consortium": SharekitMetadataExtraction.get_consortium
}


def create_objective(root=None):
    objective = {
        "@": "$.data",
        "external_id": "$.id",
        "state": SharekitMetadataExtraction.get_record_state
    }
    objective.update(SHAREKIT_EXTRACTION_OBJECTIVE)
    if root:
        objective["@"] = root
    return objective
