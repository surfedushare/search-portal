import re
from hashlib import sha1
from mimetypes import guess_type

import vobject
from dateutil.parser import parse as date_parser
from django.conf import settings
from django.utils.text import slugify


class HanDataExtraction(object):

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

    @classmethod
    def find_resources(cls, xml, resource_type):
        resource_code = None
        if resource_type == "file":
            resource_code = "objectFile"
        elif resource_type == "link":
            resource_code = "humanStartPage"
        elif resource_type == "meta":
            resource_code = "descriptiveMetadata"
        resource_identifier = f"info:eu-repo/semantics/{resource_code}"
        return xml.find_all("rdf:type", attrs={"rdf:resource": resource_identifier})

    @classmethod
    def find_metadata(cls, xml):
        resources = cls.find_resources(xml, "meta")
        if not resources:
            return
        elif len(resources) > 1:
            raise AssertionError(f"Unexpected length for metadata resource: {len(resources)}")
        metadata = resources[0]
        item = next((parent for parent in metadata.parents if parent.name == "didl:item"), None)
        if not item:
            raise AssertionError("Metadata descriptor did not have an item as parent")
        return item.find("didl:resource")

    @classmethod
    def get_files(cls, soup, el):
        file_resources = cls.find_resources(el, "file")
        link_resources = cls.find_resources(el, "link")
        resources = file_resources + link_resources
        results = []
        for resource in resources:
            item = next((parent for parent in resource.parents if parent.name == "didl:item"), None)
            if not item:
                continue
            element = item.find("didl:resource")
            if element:
                url = element["ref"]
                results.append({
                    "mime_type": element["mimetype"],
                    "url": url,
                    "hash": sha1(url.encode("utf-8")).hexdigest(),
                    "title": None
                })
        return results

    @classmethod
    def get_url(cls, soup, el):
        files = cls.get_files(soup, el)
        if not len(files):  # happens when a record was deleted
            return
        return files[0]["url"].strip()

    @classmethod
    def get_mime_type(cls, soup, el):
        files = cls.get_files(soup, el)
        if not len(files):  # happens when a record was deleted
            return
        return files[0]["mime_type"].strip()

    @classmethod
    def get_copyright(cls, soup, el):
        metadata = cls.find_metadata(el)
        if not metadata:
            return
        copyright_element = metadata.find("mods:accesscondition")
        if not copyright_element:
            return
        return "no" if "openAccess" in copyright_element["type"] else "yes"

    @classmethod
    def get_language(cls, soup, el):
        return None

    @classmethod
    def get_title(cls, soup, el):
        node = el.find('mods:title')
        return node.text.strip() if node else None

    @classmethod
    def get_keywords(cls, soup, el):
        nodes = el.find_all('czp:keyword')
        return [
            node.find('czp:langstring').text.strip()
            for node in nodes
        ]

    @classmethod
    def get_description(cls, soup, el):
        node = el.find('mods:abstract')
        return node.text if node else None

    @classmethod
    def get_authors(cls, soup, el):
        roles = el.find_all(string='aut')
        if not roles:
            return []
        authors = []
        for role in roles:
            author = role.find_parent('mods:name')
            if not author:
                continue
            name = author.find('mods:displayform')
            if not name:
                continue
            authors.append({
                "name": name.text.strip(),
                "email": None,
                "external_id": None,
                "dai": None,
                "orcid": None,
                "isni": None,
            })
        return authors

    @classmethod
    def get_publishers(cls, soup, el):
        return [
            publisher.text.strip()
            for publisher in el.find_all('mods:publisher') if publisher.text.strip()
        ]

    @classmethod
    def get_publisher_date(cls, soup, el):
        datetime = el.find("dcterms:modified")
        return datetime.text.strip() if datetime else None

    @classmethod
    def get_publisher_year(cls, soup, el):
        year = el.find("mods:dateissued")
        return year.text.strip() if year else None

    @classmethod
    def get_technical_type(cls, soup, el):
        mime_type = cls.get_mime_type(soup, el)
        if mime_type:
            return settings.MIME_TYPE_TO_TECHNICAL_TYPE.get(mime_type, "unknown")
        return

    @classmethod
    def get_from_youtube(cls, soup, el):
        url = cls.get_url(soup, el)
        if not url:
            return False
        return cls.youtube_regex.match(url) is not None

    @classmethod
    def get_is_restricted(cls, soup, el):
        return False

    @classmethod
    def get_analysis_allowed(cls, soup, el):
        # We disallow analysis for non-derivative materials as we'll create derivatives in that process
        # NB: any material that is_restricted will also have analysis_allowed set to False
        copyright = HanDataExtraction.get_copyright(soup, el)
        return (copyright is not None and "nd" not in copyright) and copyright != "yes"

    @classmethod
    def get_research_object_type(cls, soup, el):
        genre = el.find("mods:genre")
        return genre.text.strip() if genre else None

    @classmethod
    def get_doi(cls, soup, el):
        dois = [
            url_identifier.text.strip()
            for url_identifier in el.find_all("mods:identifier", attrs={"type": "uri"})
            if "doi.org" in url_identifier.text
        ]
        return dois[0] if len(dois) else None

    @classmethod
    def get_lowest_educational_level(cls, soup, el):
        return 3


HAN_EXTRACTION_OBJECTIVE = {
    # Essential NPPO properties
    "url": HanDataExtraction.get_url,
    "files": HanDataExtraction.get_files,
    "copyright": HanDataExtraction.get_copyright,
    "title": HanDataExtraction.get_title,
    "language": HanDataExtraction.get_language,
    "keywords": lambda soup, el: [],
    "description": HanDataExtraction.get_description,
    "mime_type": HanDataExtraction.get_mime_type,
    "authors": HanDataExtraction.get_authors,
    "publishers": HanDataExtraction.get_publishers,
    "publisher_date": HanDataExtraction.get_publisher_date,
    "publisher_year": HanDataExtraction.get_publisher_year,

    # Non-essential NPPO properties
    "technical_type": HanDataExtraction.get_technical_type,
    "from_youtube": HanDataExtraction.get_from_youtube,
    "is_restricted": HanDataExtraction.get_is_restricted,
    "analysis_allowed": HanDataExtraction.get_analysis_allowed,
    "research_object_type": HanDataExtraction.get_research_object_type,
    "research_themes": lambda soup, el: None,
    "parties": lambda soup, el: [],
    "doi": HanDataExtraction.get_doi,

    # Non-essential Edusources properties (for compatibility reasons)
    "material_types": lambda soup, el: None,
    "aggregation_level": lambda soup, el: None,
    "lom_educational_levels": lambda soup, el: [],
    "disciplines": lambda soup, el: [],
    "ideas": lambda soup, el: [],
    "is_part_of": lambda soup, el: [],
    "has_parts": lambda soup, el: [],
    "copyright_description": lambda soup, el: None,
    "learning_material_themes": lambda soup, el: [],
    "consortium": lambda soup, el: None,
    "lom_educational_level": lambda soup, el: None,
    "lowest_educational_level": HanDataExtraction.get_lowest_educational_level,  # TODO: make tests run as NPPO
}
