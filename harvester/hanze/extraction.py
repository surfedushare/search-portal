import re
from mimetypes import guess_type
from hashlib import sha1

from django.conf import settings

from datagrowth.processors import ExtractProcessor


class HanzeResourceObjectExtraction(ExtractProcessor):

    youtube_regex = re.compile(r".*(youtube\.com|youtu\.be).*", re.IGNORECASE)

    @classmethod
    def get_record_state(cls, node):
        return "active"

    #############################
    # GENERIC
    #############################

    @staticmethod
    def _parse_electronic_version(electronic_version):
        if "file" in electronic_version:
            url = electronic_version["file"]["fileURL"]
        elif "link" in electronic_version:
            url = electronic_version["link"]
        else:
            return
        return {
            "title": None,
            "url": url,
            "mime_type": None,
            "hash": sha1(url.encode("utf-8")).hexdigest()
        }

    @classmethod
    def get_files(cls, node):
        if "electronicVersions" not in node:
            return []
        return [
            cls._parse_electronic_version(electronic_version)
            for electronic_version in node["electronicVersions"] if cls._parse_electronic_version(electronic_version)
        ]

    @classmethod
    def get_language(cls, node):
        language = node["language"]["term"]["text"][0]["value"]
        if language == "Nederlands":
            return "nl"
        elif language == "Engels":
            return "en"
        return "unk"

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
    def get_copyright(cls, node):
        return "cc-by-40"

    @classmethod
    def get_from_youtube(cls, node):
        url = cls.get_url(node)
        if not url:
            return False
        return cls.youtube_regex.match(url) is not None

    @classmethod
    def get_authors(cls, node):
        return [
            {
                "name": None,
                "email": None,
                "external_id": person["person"]["uuid"],
                "dai": None,
                "orcid": None,
                "isni": None
            }
            for person in node["personAssociations"] if person
        ]

    @classmethod
    def get_publishers(cls, node):
        return ["Hanze"]

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
        return 2

    @classmethod
    def get_is_restricted(cls, node):
        return False

    @classmethod
    def get_analysis_allowed(cls, node):
        return True

    @classmethod
    def get_empty_list(cls, node):
        return []

    @classmethod
    def get_none(cls, node):
        return None

    @classmethod
    def get_learning_material_themes(cls, node):
        theme_value = node["attributes"].get("themesLearningMaterial", [])
        if not theme_value:
            return []
        return theme_value if isinstance(theme_value, list) else [theme_value]


HANZE_EXTRACTION_OBJECTIVE = {
    "url": HanzeResourceObjectExtraction.get_url,
    "files": HanzeResourceObjectExtraction.get_files,
    "title": "$.title.value",
    "language": HanzeResourceObjectExtraction.get_language,
    "keywords": HanzeResourceObjectExtraction.get_empty_list,
    "description": "$.abstract.text.0.value",
    "mime_type": HanzeResourceObjectExtraction.get_mime_type,
    "technical_type": HanzeResourceObjectExtraction.get_technical_type,
    "material_types": HanzeResourceObjectExtraction.get_empty_list,
    "copyright": HanzeResourceObjectExtraction.get_copyright,
    "copyright_description": HanzeResourceObjectExtraction.get_none,
    "aggregation_level": HanzeResourceObjectExtraction.get_none,
    "authors": HanzeResourceObjectExtraction.get_authors,
    "publishers": HanzeResourceObjectExtraction.get_publishers,
    "publisher_date": "$.publicationStatuses.0.publicationDate.year",
    "lom_educational_levels": HanzeResourceObjectExtraction.get_empty_list,
    "lowest_educational_level": HanzeResourceObjectExtraction.get_lowest_educational_level,
    "disciplines": HanzeResourceObjectExtraction.get_empty_list,
    "ideas": HanzeResourceObjectExtraction.get_empty_list,
    "from_youtube": HanzeResourceObjectExtraction.get_from_youtube,
    "#is_restricted": HanzeResourceObjectExtraction.get_is_restricted,
    "analysis_allowed": HanzeResourceObjectExtraction.get_analysis_allowed,
    "is_part_of": HanzeResourceObjectExtraction.get_empty_list,
    "has_parts": HanzeResourceObjectExtraction.get_empty_list,
    "doi": HanzeResourceObjectExtraction.get_none,
    "research_object_type": HanzeResourceObjectExtraction.get_none,
    "research_themes": HanzeResourceObjectExtraction.get_empty_list,
    "parties": HanzeResourceObjectExtraction.get_empty_list,
    "learning_material_themes": HanzeResourceObjectExtraction.get_empty_list,
    "consortium": HanzeResourceObjectExtraction.get_none
}
