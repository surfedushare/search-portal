import re
from mimetypes import guess_type
from hashlib import sha1

from django.conf import settings

from datagrowth.processors import ExtractProcessor

from sources.extraction.hanze.research_themes import ASJC_TO_RESEARCH_THEME


class HanzeResourceObjectExtraction(ExtractProcessor):

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
        return "open-access"

    @classmethod
    def get_description(cls, node):
        if "abstract" not in node:
            return
        return next(iter(node["abstract"].values()), None)

    @classmethod
    def get_from_youtube(cls, node):
        url = cls.get_url(node)
        if not url:
            return False
        return cls.youtube_regex.match(url) is not None

    @classmethod
    def get_authors(cls, node):
        authors = []
        for person in node["contributors"]:
            name = person.get('name', {})
            match name:
                case {"firstName": first_name}:
                    full_name = f"{first_name} {name['lastName']}"
                case {"lastName": last_name}:
                    full_name = last_name
                case _:
                    full_name = None
            authors.append({
                "name": full_name,
                "email": None,
                "external_id": person.get("person", {}).get("uuid", None),
                "dai": None,
                "orcid": None,
                "isni": None
            })
        return authors

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
    def get_is_restricted(cls, node):
        electronic_versions = node.get("electronicVersions", [])
        if not electronic_versions:
            return True
        main_file = electronic_versions[0]
        access = main_file.get("accessType", {}).get("term", {}).get("en_GB", None)
        return access != "Open"

    @classmethod
    def get_analysis_allowed(cls, node):
        # We disallow analysis for non-derivative materials as we'll create derivatives in that process
        # NB: any material that is_restricted will also have analysis_allowed set to False
        copyright = HanzeResourceObjectExtraction.get_copyright(node)
        return (copyright is not None and "nd" not in copyright) and copyright != "yes"

    @classmethod
    def get_doi(cls, node):
        if "electronicVersions" not in node:
            return None
        doi_version = next(
            (electronic_version for electronic_version in node["electronicVersions"] if "doi" in electronic_version),
            None
        )
        return doi_version["doi"] if doi_version else None

    @classmethod
    def get_research_themes(cls, node):
        research_themes = []
        for keywords in node.get("keywordGroups", []):
            if keywords["logicalName"] == "ASJCSubjectAreas":
                asjc_identifiers = [
                    classification["uri"].replace("/dk/atira/pure/subjectarea/asjc/", "")
                    for classification in keywords["classifications"]
                ]
                research_themes += [ASJC_TO_RESEARCH_THEME[identifier] for identifier in asjc_identifiers]
        return research_themes


HanzeResourceObjectExtraction.OBJECTIVE = {
    # Essential NPPO properties
    "url": HanzeResourceObjectExtraction.get_url,
    "files": HanzeResourceObjectExtraction.get_files,
    "copyright": HanzeResourceObjectExtraction.get_copyright,
    "title": "$.title.value",
    "language": HanzeResourceObjectExtraction.get_language,
    "keywords": "$.keywordGroups.0.keywords.0.freeKeywords",
    "description": HanzeResourceObjectExtraction.get_description,
    "mime_type": HanzeResourceObjectExtraction.get_mime_type,
    "authors": HanzeResourceObjectExtraction.get_authors,
    "publishers": HanzeResourceObjectExtraction.get_publishers,
    "publisher_date": lambda node: None,
    "publisher_year": "$.publicationStatuses.0.publicationDate.year",

    # Non-essential NPPO properties
    "technical_type": HanzeResourceObjectExtraction.get_technical_type,
    "from_youtube": HanzeResourceObjectExtraction.get_from_youtube,
    "is_restricted": HanzeResourceObjectExtraction.get_is_restricted,
    "analysis_allowed": HanzeResourceObjectExtraction.get_analysis_allowed,
    "research_object_type": "$.type.term.en_GB",
    "research_themes": HanzeResourceObjectExtraction.get_research_themes,
    "parties": lambda node: [],
    "doi": HanzeResourceObjectExtraction.get_doi,

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
