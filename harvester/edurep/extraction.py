import re
import vobject
from html import unescape
from mimetypes import guess_type

from django.conf import settings
from django.utils.text import slugify

from core.constants import HIGHER_EDUCATION_LEVELS, RESTRICTED_MATERIAL_SETS


class EdurepDataExtraction(object):

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
        card = unescape(el.text.strip())
        card = "\n".join(field.strip() for field in card.split("\n"))
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
        assert output_type in ["czp:entry", "czp:id"]
        entries = element.find_all(string=classification_type)
        blocks = []
        for entry in entries:
            classification_element = entry.find_parent('czp:classification')
            if not classification_element:
                continue
            blocks += classification_element.find_all(output_type)
        return blocks

    @classmethod
    def get_files(cls, soup, el):
        mime_types = el.find_all('czp:format')
        urls = el.find_all('czp:location')
        return list(
            zip(
                [mime_node.text.strip() for mime_node in mime_types],
                [url_node.text.strip() for url_node in urls],
                [f"URL {ix+1}" for ix, mime_node in enumerate(mime_types)],
            )
        )

    @classmethod
    def get_url(cls, soup, el):
        files = cls.get_files(soup, el)
        if not len(files):  # happens when a record was deleted
            return
        # Takes the first html file to be the main file and otherwise the first file
        main_url = next(
            (url for mime_type, url, name in files if mime_type == "text/html"),
            files[0][1]
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
        node = el.find('czp:title')
        if node is None:
            return
        translation = node.find('czp:langstring')
        return unescape(translation.text.strip()) if translation else None

    @classmethod
    def get_language(cls, soup, el):
        node = el.find('czp:language')
        return node.text.strip() if node else None

    @classmethod
    def get_keywords(cls, soup, el):
        nodes = el.find_all('czp:keyword')
        return [
            unescape(node.find('czp:langstring').text.strip())
            for node in nodes
        ]

    @classmethod
    def get_description(cls, soup, el):
        node = el.find('czp:description')
        if node is None:
            return
        translation = node.find('czp:langstring')
        return unescape(translation.text) if translation else None

    @classmethod
    def get_mime_type(cls, soup, el):
        node = el.find('czp:format')
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
    def get_material_types(cls, soup, el):
        material_types = el.find_all('czp:learningresourcetype')
        if not material_types:
            return []
        return [
            material_type.find('czp:value').find('czp:langstring').text.strip()
            for material_type in material_types
        ]

    @classmethod
    def get_copyright(cls, soup, el):
        node = el.find('czp:copyrightandotherrestrictions')
        if node is None:
            return
        copyright = node.find('czp:value').find('czp:langstring').text.strip()
        if copyright == "yes":
            copyright = cls.parse_copyright_description(cls.get_copyright_description(soup, el))
        return copyright

    @classmethod
    def get_aggregation_level(cls, soup, el):
        node = el.find('czp:aggregationlevel', None)
        if node is None:
            return None
        return node.find('czp:value').find('czp:langstring').text.strip() if node else None

    @classmethod
    def get_authors(cls, soup, el):
        author = el.find(string='author')
        if not author:
            return []
        contribution = author.find_parent('czp:contribute')
        if not contribution:
            return []
        nodes = contribution.find_all('czp:vcard')

        authors = []
        for node in nodes:
            author = cls.parse_vcard_element(node)
            if hasattr(author, "fn"):
                authors.append({
                    "name": author.fn.value,
                    "email": None
                })
        return authors

    @classmethod
    def get_publishers(cls, soup, el):
        publishers = []
        # Check HBOVPK tags
        hbovpk_keywords = [keyword for keyword in cls.get_keywords(soup, el) if "hbovpk" in keyword.lower()]
        if hbovpk_keywords:
            publishers.append("HBO Verpleegkunde")
        # Look at actual publishers
        publisher_element = el.find(string='publisher')
        if not publisher_element:
            return publishers
        contribution_element = publisher_element.find_parent('czp:contribute')
        if not contribution_element:
            return publishers
        nodes = contribution_element.find_all('czp:vcard')
        for node in nodes:
            publisher = cls.parse_vcard_element(node)
            if hasattr(publisher, "fn"):
                publishers.append(publisher.fn.value)

        return publishers

    @classmethod
    def get_publisher_date(cls, soup, el):
        publisher = el.find(string='publisher')
        if not publisher:
            return
        contribution = publisher.find_parent('czp:contribute')
        if not contribution:
            return
        datetime = contribution.find('czp:datetime')
        if not datetime:
            return
        return datetime.text.strip()

    @classmethod
    def get_lom_educational_levels(cls, soup, el):
        educational = el.find('czp:educational')
        if not educational:
            return []
        contexts = educational.find_all('czp:context')
        if not contexts:
            return []
        educational_levels = [
            edu.find('czp:value').find('czp:langstring').text.strip()
            for edu in contexts
        ]
        return list(set(educational_levels))

    @classmethod
    def get_lowest_educational_level(cls, soup, el):
        educational_levels = cls.get_lom_educational_levels(soup, el)
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
    def get_disciplines(cls, soup, el):
        blocks = cls.find_all_classification_blocks(el, "discipline", "czp:id")
        return list(set([block.text.strip() for block in blocks]))

    @classmethod
    def get_ideas(cls, soup, el):
        external_id = cls.get_oaipmh_external_id(soup, el)
        if not external_id.startswith("surfsharekit"):
            return []
        blocks = cls.find_all_classification_blocks(el, "idea", "czp:entry")
        compound_ideas = list(set([block.find('czp:langstring').text.strip() for block in blocks]))
        ideas = []
        for compound_idea in compound_ideas:
            ideas += compound_idea.split(" - ")
        return list(set(ideas))

    @classmethod
    def get_is_restricted(cls, soup, el):
        # We don't have access to restricted materials so we disallow analysis for them
        external_id = cls.get_oaipmh_external_id(soup, el)
        for restricted_set in RESTRICTED_MATERIAL_SETS:
            if external_id.startswith(restricted_set + ":"):
                return True
        return False

    @classmethod
    def get_analysis_allowed(cls, soup, el):
        # We disallow analysis for non-derivative materials as we'll create derivatives in that process
        # NB: any material that is_restricted will also have analysis_allowed set to False
        copyright = EdurepDataExtraction.get_copyright(soup, el)
        return (copyright is not None and "nd" not in copyright) and copyright != "yes"

    @classmethod
    def get_is_part_of(cls, soup, el):
        return []  # not supported for now

    @classmethod
    def get_has_parts(cls, soup, el):
        return []  # not supported for now

    @classmethod
    def get_copyright_description(cls, soup, el):
        node = el.find('czp:rights')
        if not node:
            return
        description = node.find('czp:description')
        return description.find('czp:langstring').text.strip() if description else None


EDUREP_EXTRACTION_OBJECTIVE = {
    "url": EdurepDataExtraction.get_url,
    "files": EdurepDataExtraction.get_files,
    "title": EdurepDataExtraction.get_title,
    "language": EdurepDataExtraction.get_language,
    "keywords": EdurepDataExtraction.get_keywords,
    "description": EdurepDataExtraction.get_description,
    "mime_type": EdurepDataExtraction.get_mime_type,
    "technical_type": EdurepDataExtraction.get_technical_type,
    "material_types": EdurepDataExtraction.get_material_types,
    "copyright": EdurepDataExtraction.get_copyright,
    "aggregation_level": EdurepDataExtraction.get_aggregation_level,
    "authors": EdurepDataExtraction.get_authors,
    "publishers": EdurepDataExtraction.get_publishers,
    "publisher_date": EdurepDataExtraction.get_publisher_date,
    "lom_educational_levels": EdurepDataExtraction.get_lom_educational_levels,
    "lowest_educational_level": EdurepDataExtraction.get_lowest_educational_level,
    "disciplines": EdurepDataExtraction.get_disciplines,
    "ideas": EdurepDataExtraction.get_ideas,
    "from_youtube": EdurepDataExtraction.get_from_youtube,
    "is_restricted": EdurepDataExtraction.get_is_restricted,
    "analysis_allowed": EdurepDataExtraction.get_analysis_allowed,
    "is_part_of": EdurepDataExtraction.get_is_part_of,
    "has_parts": EdurepDataExtraction.get_has_parts,
    "copyright_description": EdurepDataExtraction.get_copyright_description,
    "doi": lambda soup, el: None,
    "research_object_type": lambda soup, el: None,
    "research_themes": lambda soup, el: None,
    "parties": lambda soup, el: [],
}
