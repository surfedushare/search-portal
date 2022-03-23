import re
from mimetypes import guess_type
from hashlib import sha1
from dateutil.parser import parse as date_parser

from django.conf import settings

from datagrowth.processors import ExtractProcessor


class HkuMetadataExtraction(ExtractProcessor):

    youtube_regex = re.compile(r".*(youtube\.com|youtu\.be).*", re.IGNORECASE)

    @classmethod
    def get_record_state(cls, node):
        return "deleted" if node["deleted"] else "active"

    #############################
    # GENERIC
    #############################

    @classmethod
    def get_files(cls, node):
        document = node["document"]
        if not document:
            return []
        file_object = document["file"]
        return [
            {
                "title": file_object["title"],
                "url": file_object["raw"],
                "mime_type": None,
                "hash": sha1(file_object["raw"].encode("utf-8")).hexdigest()
            }
        ]

    @classmethod
    def get_language(cls, node):
        language = node["language"]
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
        return [{
            "name": node["author"],
            "email": None,
            "external_id": None,
            "dai": None,
            "orcid": None,
            "isni": None
        }]

    @classmethod
    def get_publisher_year(cls, node):
        datetime = date_parser(node["date"])
        return datetime.year

    @classmethod
    def get_publishers(cls, node):
        return ["Hogeschool voor de Kunsten Utrecht"]

    @classmethod
    def get_is_restricted(cls, node):
        return False

    @classmethod
    def get_analysis_allowed(cls, node):
        # We disallow analysis for non-derivative materials as we'll create derivatives in that process
        # NB: any material that is_restricted will also have analysis_allowed set to False
        copyright = HkuMetadataExtraction.get_copyright(node)
        return (copyright is not None and "nd" not in copyright) and copyright != "yes"


HKU_EXTRACTION_OBJECTIVE = {
    # Essential NPPO properties
    "url": HkuMetadataExtraction.get_url,
    "files": HkuMetadataExtraction.get_files,
    "copyright": HkuMetadataExtraction.get_copyright,
    "title": "$.title",
    "language": HkuMetadataExtraction.get_language,
    "keywords": lambda node: [],
    "description": "$.description",
    "mime_type": HkuMetadataExtraction.get_mime_type,
    "authors": HkuMetadataExtraction.get_authors,
    "publishers": HkuMetadataExtraction.get_publishers,
    "publisher_date": "$.datelastmodified",
    "publisher_year": HkuMetadataExtraction.get_publisher_year,

    # Non-essential NPPO properties
    "technical_type": HkuMetadataExtraction.get_technical_type,
    "from_youtube": HkuMetadataExtraction.get_from_youtube,
    "is_restricted": HkuMetadataExtraction.get_is_restricted,
    "analysis_allowed": HkuMetadataExtraction.get_analysis_allowed,
    "research_object_type": lambda node: None,
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
