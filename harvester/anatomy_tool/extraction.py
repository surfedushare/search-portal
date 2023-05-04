import re
import vobject
from mimetypes import guess_type
from hashlib import sha1
from dateutil.parser import parse as date_parser

from django.conf import settings
from django.utils.text import slugify


class AnatomyToolExtraction(object):

    youtube_regex = re.compile(r".*(youtube\.com|youtu\.be).*", re.IGNORECASE)
    cc_url_regex = re.compile(r"^https?://creativecommons\.org/(?P<type>\w+)/(?P<license>[a-z\-]+)/(?P<version>\d\.\d)",
                              re.IGNORECASE)
    cc_code_regex = re.compile(r"^cc([ \-][a-z]{2})+$", re.IGNORECASE)

    #############################
    # OAI-PMH
    #############################

    @classmethod
    def parse_copyright_description(cls, description):
        if description is None:
            return
        elif description == "Public Domain":
            return "pdm-10"
        elif description == "Copyrighted":
            return "yes"
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

    @staticmethod
    def parse_vcard_element(el):
        card = "\n".join(field.strip() for field in el.text.strip().split("\n"))
        card = card.replace("BEGIN:VCARD - VERSION:3.0 -", "BEGIN:VCARD\nVERSION:3.0")
        return vobject.readOne(card)

    @classmethod
    def get_oaipmh_records(cls, soup):
        return soup.find_all('record')

    @classmethod
    def get_oaipmh_external_id(cls, soup, el):
        return el.find('identifier').text.strip()

    @classmethod
    def get_oaipmh_record_state(cls, soup, el):
        header = el.find('header')
        return header.get("status", "active")

    #############################
    # GENERIC
    #############################

    @staticmethod
    def find_all_classification_blocks(element, classification_type, output_type):
        assert output_type in ["entry", "id"]
        entries = element.find_all(string=classification_type)
        blocks = []
        for entry in entries:
            classification_element = entry.find_parent('classification')
            if not classification_element:
                continue
            blocks += classification_element.find_all(output_type)
        return blocks

    @classmethod
    def get_files(cls, soup, el):
        mime_types = el.find_all('format')
        urls = el.find_all('location')
        default_copyright = cls.get_copyright(soup, el)
        return [
            {
                "mime_type": mime_type,
                "url": url,
                "hash": sha1(url.encode("utf-8")).hexdigest(),
                "title": title,
                "copyright": default_copyright,
                "access_rights": "OpenAccess" if default_copyright != "yes" else "RestrictedAccess"
            }
            for mime_type, url, title in zip(
                [mime_node.text.strip() for mime_node in mime_types],
                [url_node.text.strip() for url_node in urls],
                [f"URL {ix+1}" for ix, mime_node in enumerate(mime_types)],
            )
        ]

    @classmethod
    def get_url(cls, soup, el):
        files = cls.get_files(soup, el)
        if not len(files):  # happens when a record was deleted
            return
        # Takes the first html file to be the main file and otherwise the first file
        main_url = next(
            (file["url"] for file in files if file["mime_type"] == "text/html"),
            files[0]["url"]
        )
        return main_url.strip()

    @classmethod
    def get_from_youtube(cls, soup, el):
        url = cls.get_url(soup, el)
        if not url:
            return False
        return cls.youtube_regex.match(url) is not None

    @classmethod
    def get_title(cls, soup, el):
        node = el.find('title')
        if node is None:
            return
        translation = node.find('string')
        return translation.text.strip() if translation else None

    @classmethod
    def get_language(cls, soup, el):
        node = el.find('language')
        return node.text.strip() if node else None

    @classmethod
    def get_keywords(cls, soup, el):
        general = el.find('general')
        if not general:
            return []
        nodes = general.find_all('keyword')
        return [
            node.find('string').text.strip()
            for node in nodes if node.find('string').text
        ]

    @classmethod
    def get_description(cls, soup, el):
        node = el.find('description')
        if node is None:
            return
        translation = node.find('string')
        return translation.text if translation else None

    @classmethod
    def get_mime_type(cls, soup, el):
        node = el.find('format')
        if node:
            return node.text.strip()
        url = cls.get_url(soup, el)
        if not url:
            return
        mime_type, encoding = guess_type(url)
        return mime_type

    @classmethod
    def get_technical_type(cls, soup, el):
        mime_type = cls.get_mime_type(soup, el)
        if mime_type:
            return settings.MIME_TYPE_TO_TECHNICAL_TYPE.get(mime_type, "unknown")
        return

    @classmethod
    def get_copyright(cls, soup, el):
        return cls.parse_copyright_description(cls.get_copyright_description(soup, el)) or "yes"

    @classmethod
    def get_aggregation_level(cls, soup, el):
        node = el.find('aggregationlevel', None)
        if node is None:
            return None
        return node.find('value').text.strip() if node else None

    @classmethod
    def get_authors(cls, soup, el):
        lifecycle = el.find('lifecycle')
        if not lifecycle:
            return []
        nodes = lifecycle.find_all('entity')

        authors = []
        for node in nodes:
            author = cls.parse_vcard_element(node)
            if hasattr(author, "fn"):
                authors.append({
                    "name": author.fn.value.strip(),
                    "email": None,
                    "external_id": None,
                    "dai": None,
                    "orcid": None,
                    "isni": None,
                })
        return authors

    @classmethod
    def get_provider(cls, soup, el):
        return {
            "ror": None,
            "external_id": None,
            "slug": "anatomy_tool",
            "name": "AnatomyTOOL"
        }

    @classmethod
    def get_organizations(cls, soup, el):
        root = cls.get_provider(soup, el)
        root["type"] = "consortium"
        return {
            "root": root,
            "departments": [],
            "associates": []
        }

    @classmethod
    def get_publishers(cls, soup, el):
        return ["AnatomyTOOL"]

    @classmethod
    def get_consortium(cls, soup, el):
        return "AnatomyTOOL"

    @classmethod
    def get_publisher_date(cls, soup, el):
        publisher = el.find(string='Created')
        if not publisher:
            return
        contribution = publisher.find_parent('contribute')
        if not contribution:
            return
        datetime = contribution.find('datetime')
        if not datetime:
            return
        return datetime.text.strip()

    @classmethod
    def get_publisher_year(cls, soup, el):
        publisher_date = cls.get_publisher_date(soup, el)
        if publisher_date is None:
            return
        datetime = date_parser(publisher_date)
        return datetime.year

    @classmethod
    def get_lom_educational_levels(cls, soup, el):
        return ["HBO", "WO"]

    @classmethod
    def get_lowest_educational_level(cls, soup, el):
        return 2  # HBO

    @classmethod
    def get_studies(cls, soup, el):
        blocks = cls.find_all_classification_blocks(el, "discipline", "id")
        return list(set([block.text.strip() for block in blocks]))

    @classmethod
    def get_ideas(cls, soup, el):
        return []

    @classmethod
    def get_is_restricted(cls, soup, el):
        return False

    @classmethod
    def get_analysis_allowed(cls, soup, el):
        files = cls.get_files(soup, el)
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
    def get_is_part_of(cls, soup, el):
        return []  # not supported for now

    @classmethod
    def get_has_parts(cls, soup, el):
        return []  # not supported for now

    @classmethod
    def get_copyright_description(cls, soup, el):
        node = el.find('rights')
        if not node:
            return
        description = node.find('description')
        return description.find('string').text.strip() if description else None

    @classmethod
    def get_learning_material_disciplines(cls, soup, el):
        return ["gezondheid"]


ANATOMY_TOOL_EXTRACTION_OBJECTIVE = {
    "url": AnatomyToolExtraction.get_url,
    "files": AnatomyToolExtraction.get_files,
    "title": AnatomyToolExtraction.get_title,
    "language": AnatomyToolExtraction.get_language,
    "keywords": AnatomyToolExtraction.get_keywords,
    "description": AnatomyToolExtraction.get_description,
    "mime_type": AnatomyToolExtraction.get_mime_type,
    "technical_type": AnatomyToolExtraction.get_technical_type,
    "material_types": lambda soup, el: [],
    "copyright": AnatomyToolExtraction.get_copyright,
    "aggregation_level": AnatomyToolExtraction.get_aggregation_level,
    "authors": AnatomyToolExtraction.get_authors,
    "provider": AnatomyToolExtraction.get_provider,
    "organizations": AnatomyToolExtraction.get_organizations,
    "publishers": AnatomyToolExtraction.get_publishers,
    "publisher_date": AnatomyToolExtraction.get_publisher_date,
    "publisher_year": AnatomyToolExtraction.get_publisher_year,
    "lom_educational_levels": AnatomyToolExtraction.get_lom_educational_levels,
    "lowest_educational_level": AnatomyToolExtraction.get_lowest_educational_level,
    "studies": AnatomyToolExtraction.get_studies,
    "ideas": AnatomyToolExtraction.get_ideas,
    "from_youtube": AnatomyToolExtraction.get_from_youtube,
    "is_restricted": AnatomyToolExtraction.get_is_restricted,
    "analysis_allowed": AnatomyToolExtraction.get_analysis_allowed,
    "is_part_of": AnatomyToolExtraction.get_is_part_of,
    "has_parts": AnatomyToolExtraction.get_has_parts,
    "copyright_description": AnatomyToolExtraction.get_copyright_description,
    "doi": lambda soup, el: None,
    "research_object_type": lambda soup, el: None,
    "research_themes": lambda soup, el: [],
    "study_vocabulary": lambda soup, el: [],
    "parties": lambda soup, el: [],
    "learning_material_disciplines": AnatomyToolExtraction.get_learning_material_disciplines,
    "consortium": AnatomyToolExtraction.get_consortium,
}
