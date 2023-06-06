import os
import re
from mimetypes import guess_type
from hashlib import sha1

from django.conf import settings

from datagrowth.processors import ExtractProcessor

from sources.extraction.hanze.research_themes import ASJC_TO_RESEARCH_THEME


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
            url = electronic_version["file"]["url"]
            file_name = electronic_version["file"]["fileName"]
            mime_type = electronic_version["file"]["mimeType"]
        elif "link" in electronic_version:
            url = electronic_version["link"]
            file_name = None
            mime_type = "text/html"
        else:
            return
        access_type = electronic_version.get("accessType", {})
        access_rights = "ClosedAccess"
        if access_type.get("uri", "").endswith("/open"):
            access_rights = "OpenAccess"
        elif access_type.get("uri", "").endswith("/restricted"):
            access_rights = "RestrictedAccess"
        return {
            "title": file_name,
            "url": url,
            "mime_type": mime_type,
            "hash": sha1(url.encode("utf-8")).hexdigest(),
            "copyright": None,
            "access_rights": access_rights
        }

    @classmethod
    def get_files(cls, node):
        electronic_versions = node.get("electronicVersions", []) + node.get("additionalFiles", [])
        if not electronic_versions:
            return []
        return [
            cls._parse_electronic_version(electronic_version)
            for electronic_version in electronic_versions if cls._parse_electronic_version(electronic_version)
        ]

    @classmethod
    def get_locale(cls, node):
        locale_uri = node["language"]["uri"]
        _, locale = os.path.split(locale_uri)
        return locale

    @classmethod
    def get_language(cls, node):
        locale = cls.get_locale(node)
        if locale in ["en_GB", "nl_NL"]:
            return locale[:2]
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
    def get_description(cls, node):
        if "abstract" not in node:
            return
        locale = cls.get_locale(node)
        fallback_description = next(iter(node["abstract"].values()), None)
        return node["abstract"].get(locale, fallback_description)

    @classmethod
    def get_keywords(cls, node):
        results = []
        for keywords in node.get("keywordGroups", []):
            match keywords["logicalName"]:
                case "keywordContainers":
                    for free_keywords in keywords["keywords"]:
                        results += free_keywords["freeKeywords"]
                case "ASJCSubjectAreas":
                    for classification in keywords["classifications"]:
                        results.append(classification["term"]["en_GB"])
                case "research_focus_areas":
                    for classification in keywords["classifications"]:
                        if classification["uri"] == "research_focus_areas/05/no_hanze_research_focus_area_applicable":
                            continue
                        elif classification["uri"] == "research_focus_areas/02g_no_research_line_applicable":
                            continue
                        results.append(classification["term"]["en_GB"])
        return list(set(results))

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
            person_data = person.get("person", person.get("externalPerson", {}))
            authors.append({
                "name": full_name,
                "email": None,
                "external_id": person_data.get("uuid", None),
                "dai": None,
                "orcid": None,
                "isni": None
            })
        # We'll put the first Hanze author as first author in the list
        # Within Publinova this person will become the owner and contact person
        first_hanze_author_index = next(
            (ix for ix, person in enumerate(node["contributors"]) if "externalPerson" not in person),
            None
        )
        if first_hanze_author_index is not None:
            first_hanze_author = authors.pop(first_hanze_author_index)
            authors = [first_hanze_author] + authors
        return authors

    @classmethod
    def get_provider(cls, node):
        return {
            "ror": None,
            "external_id": None,
            "slug": "hanze",
            "name": "Hanze",
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
        return ["Hanze"]

    @classmethod
    def get_publisher_date(cls, node):
        current_publication = next(
            (publication for publication in node["publicationStatuses"] if publication["current"]),
            None
        )
        if not current_publication:
            return
        publication_date = current_publication["publicationDate"]
        year = publication_date["year"]
        month = publication_date.get("month", 1)
        day = publication_date.get("day", 1)
        return f"{year}-{month:02}-{day:02}"

    @classmethod
    def get_publisher_year(cls, node):
        current_publication = next(
            (publication for publication in node["publicationStatuses"] if publication["current"]),
            None
        )
        if not current_publication:
            return
        return current_publication["publicationDate"]["year"]

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
    "copyright": lambda node: None,
    "title": "$.title.value",
    "language": HanzeResourceObjectExtraction.get_language,
    "keywords": HanzeResourceObjectExtraction.get_keywords,
    "description": HanzeResourceObjectExtraction.get_description,
    "mime_type": HanzeResourceObjectExtraction.get_mime_type,
    "authors": HanzeResourceObjectExtraction.get_authors,
    "provider": HanzeResourceObjectExtraction.get_provider,
    "organizations": HanzeResourceObjectExtraction.get_organizations,
    "publishers": HanzeResourceObjectExtraction.get_publishers,
    "publisher_date": HanzeResourceObjectExtraction.get_publisher_date,
    "publisher_year": HanzeResourceObjectExtraction.get_publisher_year,

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
    "study_vocabulary": lambda node: [],
    "ideas": lambda node: [],
    "is_part_of": lambda node: [],
    "has_parts": lambda node: [],
    "copyright_description": lambda node: None,
    "learning_material_disciplines": lambda node: [],
    "consortium": lambda node: None,
    "lom_educational_level": lambda node: None,
    "lowest_educational_level": lambda node: 2,
}
