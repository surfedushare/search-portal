import re
from mimetypes import guess_type
from hashlib import sha1

from django.conf import settings

from datagrowth.processors import ExtractProcessor


class BuasMetadataExtraction(ExtractProcessor):

    OBJECTIVE = None

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
            url = electronic_version["file"]["url"]
            file_name = electronic_version["file"]["fileName"]
            mime_type = electronic_version["file"]["mimeType"]
        elif "link" in electronic_version:
            url = electronic_version["link"]
            file_name = None
            mime_type = "text/html"
        else:
            return
        return {
            "title": file_name,
            "url": url,
            "mime_type": mime_type,
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
        if language == "Dutch":
            return "nl"
        elif language == "English":
            return "en"
        return "unk"

    @classmethod
    def get_url(cls, node):
        files = cls.get_files(node)
        if not files:
            return node["info"]["portalUrl"]
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
        access = node["openAccessPermission"]["term"]["text"][0]["value"]
        return "open-access" if access in ["Open", "Indeterminate", "None"] else "yes"

    @classmethod
    def get_from_youtube(cls, node):
        url = cls.get_url(node)
        if not url:
            return False
        return cls.youtube_regex.match(url) is not None

    @classmethod
    def get_authors(cls, node):
        authors = []
        for person in node["personAssociations"]:
            name = person.get('name', {})
            authors.append({
                "name": f"{name['firstName']} {name['lastName']}" if name else None,
                "email": None,
                "external_id": person["pureId"],
                "dai": None,
                "orcid": None,
                "isni": None
            })
        return authors

    @classmethod
    def get_publishers(cls, node):
        return ["Hogeschool van Amsterdam"]

    @classmethod
    def get_is_restricted(cls, node):
        return False

    @classmethod
    def get_analysis_allowed(cls, node):
        # We disallow analysis for non-derivative materials as we'll create derivatives in that process
        # NB: any material that is_restricted will also have analysis_allowed set to False
        copyright = BuasMetadataExtraction.get_copyright(node)
        return (copyright is not None and "nd" not in copyright) and copyright != "yes"


BuasMetadataExtraction.OBJECTIVE = {
    # Essential NPPO properties
    "url": BuasMetadataExtraction.get_url,
    "files": BuasMetadataExtraction.get_files,
    "copyright": BuasMetadataExtraction.get_copyright,
    "title": "$.title.value",
    "language": BuasMetadataExtraction.get_language,
    "keywords": lambda node: [],
    "description": lambda node: None,
    "mime_type": BuasMetadataExtraction.get_mime_type,
    "authors": BuasMetadataExtraction.get_authors,
    "publishers": BuasMetadataExtraction.get_publishers,
    "publisher_date": lambda node: None,
    "publisher_year": "$.publicationStatuses.0.publicationDate.year",

    # Non-essential NPPO properties
    "technical_type": BuasMetadataExtraction.get_technical_type,
    "from_youtube": BuasMetadataExtraction.get_from_youtube,
    "is_restricted": BuasMetadataExtraction.get_is_restricted,
    "analysis_allowed": BuasMetadataExtraction.get_analysis_allowed,
    "research_object_type": "$.type.term.text.0.value",
    "research_themes": lambda node: [],
    "parties": lambda node: [],
    "doi": lambda node: None,

    # Non-essential Edusources properties (for compatibility reasons)
    "material_types": lambda node: None,
    "aggregation_level": lambda node: None,
    "lom_educational_levels": lambda node: [],
    "disciplines": lambda node: [],
    "ideas": lambda node: [],
    "is_part_of": lambda node: [],
    "has_parts": lambda node: [],
    "copyright_description": lambda node: None,
    "learning_material_themes": lambda node: [],
    "consortium": lambda node: None,
    "lom_educational_level": lambda node: None,
    "lowest_educational_level": lambda node: 2,
}
