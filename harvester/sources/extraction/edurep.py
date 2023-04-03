import re
from mimetypes import guess_type
from hashlib import sha1
from core.constants import HIGHER_EDUCATION_LEVELS
from django.conf import settings
from dateutil.parser import parse as date_parser
from datagrowth.processors import ExtractProcessor
from django.utils.text import slugify


FILE_TYPE_TO_MIME_TYPE = {
    "TEXT": "application/pdf",
    "VIDEO": "video/mp4",
    "AUDIO": "audio/mp3",
    "IMAGE": "image/jpeg",
    "DOCUMENT": "application/x-Wikiwijs-Arrangement",
    "WEBSITE": "text/html",
    "NOT_SET": None
}


class EdurepMetadataExtraction(ExtractProcessor):

    youtube_regex = re.compile(r".*(youtube\.com|youtu\.be).*", re.IGNORECASE)
    cc_url_regex = re.compile(r"^https?://creativecommons\.org/(?P<type>\w+)/(?P<license>[a-z\-]+)/(?P<version>\d\.\d)",
                              re.IGNORECASE)
    cc_code_regex = re.compile(r"^cc([ \-][a-z]{2})+$", re.IGNORECASE)

    @classmethod
    def get_record_state(cls, node):
        return "active"

    #############################
    # GENERIC
    #############################

    @staticmethod
    def _serialize_access_rights(access_rights):
        access_rights = access_rights.replace("Access", "")
        access_rights = access_rights.lower()
        access_rights += "-access"
        return access_rights

    @classmethod
    def get_files(cls, node):
        if not node:
            return []
        return {
            "title": node["schema:name"]["@value"],
            "url": node["schema:url"],
            "mime_type": FILE_TYPE_TO_MIME_TYPE.get(node["schema:encodingFormat"]),
            "hash": sha1(node["schema:url"].encode("utf-8")).hexdigest(),
            "copyright": node["schema:license"],
            "access_rights": node["dcterms:accessRights"]
        }

    @classmethod
    def get_language(cls, node):
        language = node["schema:identifier"]["schema:inLanguage"]
        if language == "Dutch":
            return "nl"
        elif language == "English":
            return "en"
        return "unk"

    @classmethod
    def get_url(cls, node):
        files = cls.get_files(node)
        if not files:
            return node["portalUrl"]
        return files[0]["url"].strip()

    @classmethod
    def get_mime_type(cls, node):
        files = cls.get_files(node)
        if not files:
            return
        return files[0]["mime_type"]

    @classmethod
    def get_technical_type(cls, node):
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
    def parse_copyright_description(cls, description):
        if description is None:
            return
        url_match = cls.cc_url_regex.match(description)
        if url_match is None:
            code_match = cls.cc_code_regex.match(description)
            return slugify(description.lower()) if code_match else None
        license = url_match.group("license").lower()
        if license == "mark":
            license = "pdm"
        elif license == "zero":
            license = "cc0"
        else:
            license = "cc-" + license
        return slugify(f"{license}-{url_match.group('version')}")

    @classmethod
    def get_copyright(cls, node):
        copyright = node["@type"]["lom:copyrightAndOtherRestrictions"]
        if copyright is None:
            return "yes"
        if copyright == "yes":
            copyright = cls.parse_copyright_description(cls.get_copyright_description(node))
        return copyright or "yes"

    @classmethod
    def get_copyright_description(cls, node):
        license = node["schema:license"]
        if not license:
            return
        return license.text.strip() if license else None

    @classmethod
    def get_from_youtube(cls, node):
        url = cls.get_url(node)
        if not url:
            return False
        return cls.youtube_regex.match(url) is not None

    @classmethod
    def get_authors(cls, node):
        authors = []
        for person in node["dcterms:creator"]:
            authors.append({
                "name": person,
                "email": None,
                "external_id": None,
                "dai": None,
                "orcid": None,
                "isni": None
            })
        return authors

    @classmethod
    def get_educational_levels(cls, node):
        blocks = node["schema:educationalLevel"]
        educational_levels = []
        for block in blocks:
            for item in block["schema:name"]:
                if item["@value"] in HIGHER_EDUCATION_LEVELS.keys():
                    educational_levels.append(item["@value"])
        return educational_levels

    @classmethod
    def get_lowest_educational_level(cls, node):
        educational_levels = cls.get_educational_levels(node)
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
    def get_provider(cls, node):
        provider_name = None
        publishers = node["dcterms:publisher"]
        if len(publishers):
            provider_name = publishers[0]
        return {
            "ror": None,
            "external_id": None,
            "slug": None,
            "name": provider_name
        }

    @classmethod
    def get_keywords(cls, node):
        keyword_dict = node["schema:keywords"]
        return[
            keyword["@value"]
            for keyword in keyword_dict
        ]

    @classmethod
    def get_organizations(cls, node):
        root = cls.get_provider(node)
        root["type"] = "institute"
        return {
            "root": root,
            "departments": [],
            "associates": []
        }

    @classmethod
    def get_material_types(cls, node):
        material_types = node["schema:learningResourceType"]
        if not material_types:
            return []
        return [
            material_type["schema:termCode"].text.strip()
            for material_type in material_types
        ]


    @classmethod
    def get_publisher_year(cls, node):
        date = node["schema:publisherDate"]
        if date is None:
            return
        datetime = date_parser(date)
        return datetime.year

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


EDUREP_EXTRACTION_OBJECTIVE = {
    # Essential NPPO properties
    "url": EdurepMetadataExtraction.get_url,
    "files": EdurepMetadataExtraction.get_files,
    "copyright": EdurepMetadataExtraction.get_copyright,
    "title": "$.schema:name.@value",
    "language": "$.schema:identifier.schema:inLanguage",
    "keywords": EdurepMetadataExtraction.get_keywords,
    "description": "$.schema:description.@value",
    "mime_type": EdurepMetadataExtraction.get_mime_type,
    "authors": EdurepMetadataExtraction.get_authors,
    "organizations": EdurepMetadataExtraction.get_organizations,
    "publishers": "$.dcterms:publisher",
    "publisher_date": "$.schema:datePublished",
    "publisher_year": EdurepMetadataExtraction.get_publisher_year,

    # Non-essential NPPO properties
    "technical_type": EdurepMetadataExtraction.get_technical_type,
    "from_youtube": EdurepMetadataExtraction.get_from_youtube,
    "is_restricted": EdurepMetadataExtraction.get_is_restricted,
    "analysis_allowed": EdurepMetadataExtraction.get_analysis_allowed,
    "research_object_type": lambda node: [],
    "research_themes": lambda node: [],
    "parties": lambda node: [],
    "doi": lambda node: [],

    # Non-essential Edusources properties (for compatibility reasons)
    "material_types": EdurepMetadataExtraction.get_material_types,
    "aggregation_level": "$.lom:aggregationLevel",
    "lom_educational_levels": EdurepMetadataExtraction.get_educational_levels,
    "studies": lambda node: [],
    "ideas": lambda node: [],
    "is_part_of": lambda node: [],
    "has_parts": lambda node: [],
    "copyright_description": EdurepMetadataExtraction.get_copyright_description,
    "learning_material_disciplines": lambda node: [],
    "consortium": lambda node: None,
    "lom_educational_level": lambda node: None,
    "lowest_educational_level": EdurepMetadataExtraction.get_lowest_educational_level
}
