import re
from html import unescape

from core.constants import HIGHER_EDUCATION_LEVELS


class EdurepDataExtraction(object):

    vcard_regex = re.compile(r"([A-Z-]+):(.+)", re.IGNORECASE)

    @classmethod
    def parse_vcard(cls, vcard, key=None):
        # "BEGIN:VCARD FN:Edurep Delen N:;Edurep Delen VERSION:3.0 END:VCARD"
        results = dict()
        if vcard:
            lines = vcard.split("\n")
            for line in lines:
                match = cls.vcard_regex.match(line)
                if match:
                    results[match.groups()[0]] = match.groups()[1]
        return results if key is None else results.get(key, vcard)

    #############################
    # OAI-PMH
    #############################

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
            )
        )

    @classmethod
    def get_url(cls, soup, el):
        files = cls.get_files(soup, el)
        if not len(files):  # happens when a record was deleted
            return
        # Takes the first html file to be the main file and otherwise the first file
        main_url = next(
            (url for mime_type, url in files if mime_type == "text/html"),
            files[0][1]
        )
        return main_url

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
        return node.text.strip() if node else None

    @classmethod
    def get_copyright(clscls, soup, el):
        node = el.find('czp:copyrightandotherrestrictions')
        return node.find('czp:value').find('czp:langstring').text.strip() if node else None

    @classmethod
    def get_aggregation_level(clscls, soup, el):
        node = el.find('czp:aggregationlevel', None)
        if node is None:
            return None
        return node.find('czp:value').find('czp:langstring').text.strip() if node else None

    @classmethod
    def get_author(cls, soup, el):
        author = el.find(string='author')
        if not author:
            return []
        contribution = author.find_parent('czp:contribute')
        if not contribution:
            return []
        nodes = contribution.find_all('czp:vcard')
        return [
            unescape(node.text.strip())
            for node in nodes
        ]

    @classmethod
    def get_authors(cls, soup, el):
        return [cls.parse_vcard(author, "FN") for author in cls.get_author(soup, el)]

    @classmethod
    def get_publishers(cls, soup, el):
        publisher = el.find(string='publisher')
        if not publisher:
            return []
        contribution = publisher.find_parent('czp:contribute')
        if not contribution:
            return []
        nodes = contribution.find_all('czp:vcard')
        return [
            cls.parse_vcard(unescape(node.text.strip()), "FN")
            for node in nodes
        ]

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
    def get_educational_levels(cls, soup, el):
        blocks = cls.find_all_classification_blocks(el, "educational level", "czp:id")
        return list(set([block.text.strip() for block in blocks]))

    @classmethod
    def get_humanized_educational_levels(cls, soup, el):
        blocks = cls.find_all_classification_blocks(el, "educational level", "czp:entry")
        return list(set([block.find('czp:langstring').text.strip() for block in blocks]))

    @classmethod
    def get_disciplines(cls, soup, el):
        blocks = cls.find_all_classification_blocks(el, "discipline", "czp:id")
        return list(set([block.text.strip() for block in blocks]))

    @classmethod
    def get_humanized_disciplines(cls, soup, el):
        blocks = cls.find_all_classification_blocks(el, "discipline", "czp:entry")
        return list(set([block.find('czp:langstring').text.strip() for block in blocks]))
