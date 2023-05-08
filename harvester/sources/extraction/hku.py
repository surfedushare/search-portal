import re
from mimetypes import guess_type
from hashlib import sha1
from dateutil.parser import parse as date_parser

from django.conf import settings

from datagrowth.processors import ExtractProcessor


FILE_TYPE_TO_MIME_TYPE = {
    "TEXT": "application/pdf",
    "VIDEO": "video/mp4",
    "AUDIO": "audio/mp3",
    "IMAGE": "image/jpeg",
    "NOT_SET": None
}


class HkuMetadataExtraction(ExtractProcessor):

    youtube_regex = re.compile(r".*(youtube\.com|youtu\.be).*", re.IGNORECASE)

    @classmethod
    def build_product_id(cls, identifier):
        if not identifier:
            return identifier
        return f"hku:product:{identifier}"

    @classmethod
    def build_person_id(cls, identifier):
        if not identifier:
            return identifier
        return f"hku:person:{identifier}"

    @classmethod
    def build_full_name(cls, person):
        match person:
            case {"first_name": first_name, "last_name": last_name, "prefix": prefix} if person.get("prefix"):
                full_name = f"{first_name} {prefix} {last_name}"
            case {"first_name": first_name, "last_name": last_name} if person.get("first_name"):
                full_name = f"{first_name} {last_name}"
            case {"last_name": last_name}:
                full_name = last_name
            case _:
                full_name = None
        return full_name

    @classmethod
    def get_external_id(cls, node):
        identifier = node["resultid"] or None
        return cls.build_product_id(identifier)

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
        default_copyright = cls.get_copyright(node)
        file_object = document["file"]
        return [
            {
                "title": file_object["title"],
                "url": file_object["raw"],
                "mime_type": FILE_TYPE_TO_MIME_TYPE.get(file_object["type"]),
                "hash": sha1(file_object["raw"].encode("utf-8")).hexdigest(),
                "copyright": default_copyright,
                "access_rights": "OpenAccess"  # as agreed upon with an email by Emile Bijk on 1 December 2022
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
        if node["licence"] == "Niet commercieel - geen afgeleide werken (CC BY-NC-ND)":
            return "cc-by-nc-nd-40"
        return "yes"

    @classmethod
    def get_keywords(cls, node):
        tags = node["tags"]
        if not tags:
            return []
        return tags.split(", ")

    @classmethod
    def get_from_youtube(cls, node):
        url = cls.get_url(node)
        if not url:
            return False
        return cls.youtube_regex.match(url) is not None

    @classmethod
    def get_authors(cls, node):
        if not node["persons"]:
            return []
        if isinstance(node["persons"]["person"], dict):
            node["persons"]["person"] = [node["persons"]["person"]]
        return [
            {
                "name": cls.build_full_name(person),
                "email": person["email"] or None,
                "external_id": cls.build_person_id(person.get("person_id", None)),
                "dai": None,
                "orcid": None,
                "isni": None
            }
            for person in node["persons"]["person"]
        ]

    @classmethod
    def get_publisher_year(cls, node):
        datetime = date_parser(node["date"])
        return datetime.year

    @classmethod
    def get_provider(cls, node):
        return {
            "ror": None,
            "external_id": None,
            "slug": "hku",
            "name": "Hogeschool voor de Kunsten Utrecht",
        }

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
    def get_publishers(cls, node):
        return ["Hogeschool voor de Kunsten Utrecht"]

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


HKU_EXTRACTION_OBJECTIVE = {
    # Essential NPPO properties
    "url": HkuMetadataExtraction.get_url,
    "files": HkuMetadataExtraction.get_files,
    "copyright": HkuMetadataExtraction.get_copyright,
    "title": "$.title",
    "language": HkuMetadataExtraction.get_language,
    "keywords": HkuMetadataExtraction.get_keywords,
    "description": "$.description",
    "mime_type": HkuMetadataExtraction.get_mime_type,
    "authors": HkuMetadataExtraction.get_authors,
    "provider": HkuMetadataExtraction.get_provider,
    "organizations": HkuMetadataExtraction.get_organizations,
    "publishers": HkuMetadataExtraction.get_publishers,
    "publisher_date": lambda node: None,
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
    "studies": lambda node: [],
    "study_vocabulary": lambda node: [],
    "ideas": lambda node: [],
    "is_part_of": lambda node: [],
    "has_parts": lambda node: [],
    "copyright_description": lambda node: None,
    "learning_material_disciplines": lambda node: [],
    "consortium": lambda node: None,
    "lowest_educational_level": lambda node: 2,
}
