import re
from mimetypes import guess_type
from hashlib import sha1

from django.conf import settings

from datagrowth.processors import ExtractProcessor


class PublinovaMetadataExtraction(ExtractProcessor):

    youtube_regex = re.compile(r".*(youtube\.com|youtu\.be).*", re.IGNORECASE)

    @classmethod
    def get_record_state(cls, node):
        return "active"

    #############################
    # GENERIC
    #############################

    @staticmethod
    def _parse_file(file_object):
        url = file_object["url"]
        file_object["hash"] = sha1(url.encode("utf-8")).hexdigest()
        return file_object

    @classmethod
    def get_files(cls, node):
        return [
            cls._parse_file(file_object)
            for file_object in node["files"]
        ]

    @classmethod
    def get_language(cls, node):
        language = node["language"]["term"]["en_GB"]
        if language == "Dutch":
            return "nl"
        elif language == "English":
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
        return node["copyright"]

    @classmethod
    def get_keywords(cls, node):
        return [
            keyword["label"] for keyword in node["keywords"]
        ]

    @classmethod
    def get_from_youtube(cls, node):
        url = cls.get_url(node)
        if not url:
            return False
        return cls.youtube_regex.match(url) is not None

    @classmethod
    def get_authors(cls, node):
        authors = node["authors"]
        for author in authors:
            external_id = author.pop("id")
            author["external_id"] = external_id
        return authors

    @classmethod
    def get_publishers(cls, node):
        return ["Publinova"]

    @classmethod
    def get_is_restricted(cls, node):
        return False

    @classmethod
    def get_analysis_allowed(cls, node):
        # We disallow analysis for non-derivative materials as we'll create derivatives in that process
        # NB: any material that is_restricted will also have analysis_allowed set to False
        copyright = PublinovaMetadataExtraction.get_copyright(node)
        return (copyright is not None and "nd" not in copyright) and copyright != "yes"

    # @classmethod
    # def get_doi(cls, node):
    #     if "electronicVersions" not in node:
    #         return None
    #     doi_version = next(
    #         (electronic_version for electronic_version in node["electronicVersions"] if "doi" in electronic_version),
    #         None
    #     )
    #     return doi_version["doi"] if doi_version else None


PUBLINOVA_EXTRACTION_OBJECTIVE = {
    # Essential NPPO properties
    "url": PublinovaMetadataExtraction.get_url,
    "files": PublinovaMetadataExtraction.get_files,
    "copyright": PublinovaMetadataExtraction.get_copyright,
    "title": "$.title",
    # "language": PublinovaMetadataExtraction.get_language,
    "keywords": PublinovaMetadataExtraction.get_keywords,
    "description": "$.description",
    "mime_type": PublinovaMetadataExtraction.get_mime_type,
    "authors": PublinovaMetadataExtraction.get_authors,
    "publishers": PublinovaMetadataExtraction.get_publishers,
    # "publisher_date": lambda node: None,
    # "publisher_year": "$.publicationStatuses.0.publicationDate.year",

    # # Non-essential NPPO properties
    "technical_type": PublinovaMetadataExtraction.get_technical_type,
    "from_youtube": PublinovaMetadataExtraction.get_from_youtube,
    "is_restricted": PublinovaMetadataExtraction.get_is_restricted,
    "analysis_allowed": PublinovaMetadataExtraction.get_analysis_allowed,
    # "research_object_type": "$.type.term.en_GB",
    # "research_themes": lambda node: [],
    # "parties": lambda node: [],
    # "doi": PublinovaMetadataExtraction.get_doi,

    # Non-essential Edusources properties (for compatibility reasons)
    "material_types": lambda node: None,
    "aggregation_level": lambda node: None,
    "lom_educational_levels": lambda node: [],
    "studies": lambda node: [],
    "ideas": lambda node: [],
    "is_part_of": lambda node: [],
    "has_parts": lambda node: [],
    "copyright_description": lambda node: None,
    "learning_material_disciplines": lambda node: [],
    "consortium": lambda node: None,
    "lom_educational_level": lambda node: None,
    "lowest_educational_level": lambda node: 2,
}
