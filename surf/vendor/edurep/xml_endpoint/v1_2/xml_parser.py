from xml.etree import ElementTree as ET

import re

from surf.vendor.edurep.xml_endpoint.v1_2.choices import (
    MIME_TYPE_TECH_FORMAT,
    DISCIPLINE_CUSTOM_THEME
)

_NS = {
    "srw": "http://www.loc.gov/zing/srw/",
    "diag": "http://www.loc.gov/zing/srw/diagnostic/",
    "xcql": "http://www.loc.gov/zing/cql/xcql/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "meresco_srw": "http://meresco.org/namespace/srw#",
    "dd": "http://meresco.org/namespace/drilldown",
    "czp": "http://www.imsglobal.org/xsd/imsmd_v1p2",
    "sad": "http://xsd.kennisnet.nl/smd/sad"
}

TECH_FORMAT_LOM = "lom.technical.format"
DISCIPLINE_ID_LOM = "lom.classification.obk.discipline.id"
CUSTOM_THEME_ID = "custom_theme.id"


def parse_response(xml_text):
    root = ET.fromstring(xml_text)
    return dict(recordcount=_parse_number_of_records(root),
                records=_parse_records(root),
                drilldowns=_parse_drilldowns(root))


def _parse_number_of_records(root):
    try:
        return int(root.find("srw:numberOfRecords", namespaces=_NS).text)
    except Exception:
        return 0


def _parse_records(root):
    return _parse_item_list(root, "srw:records", _parse_record)


_RECORD_ID_PATH = "srw:recordIdentifier"
_TITLE_PATH = "./srw:recordData/czp:lom/czp:general/czp:title/czp:langstring"
_DESCRIPTION_PATH = "./srw:recordData/czp:lom/czp:general/czp:description/czp:langstring"
_OBJECT_ID_PATH = "./srw:recordData/czp:lom/czp:general/czp:catalogentry/czp:entry/czp:langstring"
_URL_PATH = "./srw:recordData/czp:lom/czp:technical/czp:location"
_FORMAT_PATH = "./srw:recordData/czp:lom/czp:technical/czp:format"
_KEYWORD_PATH = "./srw:recordData/czp:lom/czp:general/czp:keyword/czp:langstring"
_LANGUAGE_PATH = "./srw:recordData/czp:lom/czp:general/czp:language"
_AGGREGATIONAL_LEVEL_PATH = "./srw:recordData/czp:lom/czp:general/czp:aggregationlevel/czp:value/czp:langstring"
_PUBLISH_DATETIME_PATH = "./srw:recordData/czp:lom/czp:lifecycle/czp:contribute/czp:date/czp:datetime"
_LIFECYCLE_CONTRIBUTE_PATH = "./srw:recordData/czp:lom/czp:lifecycle/czp:contribute"
_METADATA_CONTRIBUTE_PATH = "./srw:recordData/czp:lom/czp:metametadata/czp:contribute"
_CONTRIBUTE_ROLE_PATH = "./czp:role/czp:value/czp:langstring"
_CONTRIBUTE_VCARD_PATH = "./czp:centity/czp:vcard"
_CONTRIBUTE_DATETIME_PATH = "./czp:date/czp:datetime"
_NUMBER_OF_RATINGS_PATH = "./srw:extraRecordData/recordData/sad:smbAggregatedData/sad:numberOfRatings"
_AVERAGE_RATINGS_PATH = "./srw:extraRecordData/recordData/sad:smbAggregatedData/sad:averageNormalizedRating"


def _parse_record(elem):
    contributors = _parse_contributors(elem)
    publisher = contributors.get("publisher", {}).get("name")
    publish_datetime = contributors.get("publisher", {}).get("datetime")
    author = contributors.get("author", {}).get("name")
    creator = contributors.get("creator", {}).get("name")

    return dict(
        external_id=_find_elem_text(elem, _RECORD_ID_PATH),
        object_id=_find_elem_text(elem, _OBJECT_ID_PATH),
        url=_find_elem_text(elem, _URL_PATH),
        title=_find_elem_text(elem, _TITLE_PATH),
        description=_find_elem_text(elem, _DESCRIPTION_PATH),
        keywords=_find_elems_text(elem, _KEYWORD_PATH),
        language=_find_elem_text(elem, _LANGUAGE_PATH),
        aggregationlevel=_find_elem_text(elem, _AGGREGATIONAL_LEVEL_PATH),
        publisher=publisher,
        publish_datetime=publish_datetime,
        author=author,
        creator=creator,
        format=MIME_TYPE_TECH_FORMAT.get(_find_elem_text(elem, _FORMAT_PATH)),
        number_of_ratings=int(_find_elem_text(elem, _NUMBER_OF_RATINGS_PATH)),
        average_rating=float(_find_elem_text(elem, _AVERAGE_RATINGS_PATH)),
        themes=[],
        has_bookmark=False,
        number_of_applauds=0,
        number_of_views=0,
        number_of_collections=0,
    )


_VCARD_FORMATED_NAME_KEY = "FN"


def _parse_contributors(elem):
    rv = dict()
    elements = elem.findall(_LIFECYCLE_CONTRIBUTE_PATH, namespaces=_NS)
    for e in elements:
        rv.update(_parse_contributor(e))
    elements = elem.findall(_METADATA_CONTRIBUTE_PATH, namespaces=_NS)
    for e in elements:
        rv.update(_parse_contributor(e))
    return rv


def _parse_contributor(e):
    role = _find_elem_text(e, _CONTRIBUTE_ROLE_PATH)
    vcard = _find_elem_text(e, _CONTRIBUTE_VCARD_PATH)
    dtime = _find_elem_text(e, _CONTRIBUTE_DATETIME_PATH)
    name = _parse_vcard(vcard).get(_VCARD_FORMATED_NAME_KEY)
    return {role: dict(vcard=vcard, datetime=dtime, name=name)}


item_regex = re.compile(r"([A-Z-]+):(.+)", re.IGNORECASE)


def _parse_vcard(vcard):
    # "BEGIN:VCARD FN:Edurep Delen N:;Edurep Delen VERSION:3.0 END:VCARD"
    rv = dict()
    if vcard:
        items = vcard.split("\n")
        for item in items:
            m = item_regex.match(item)
            if m:
                rv[m.groups()[0]] = m.groups()[1]
    return rv


_DRILLDOWN_PATH = "./srw:extraResponseData/dd:drilldown/dd:term-drilldown"


def _parse_drilldowns(root):
    rv = dict()
    try:
        drilldowns = root.findall(_DRILLDOWN_PATH, namespaces=_NS)[0]
        for dd in drilldowns:
            term_id = dd.attrib["name"]
            if term_id == TECH_FORMAT_LOM:
                rv[term_id] = _parse_drilldowns_tech_format(dd)
            elif term_id == DISCIPLINE_ID_LOM:
                rv[term_id] = _parse_drilldowns_term(dd)
                rv[CUSTOM_THEME_ID] = _parse_drilldowns_custom_theme(dd)
            else:
                rv[term_id] = _parse_drilldowns_term(dd)
    except Exception as e:
        pass
    return [dict(external_id=k, items=v) for k, v in rv.items()]


def _parse_drilldowns_term(elem):
    return [dict(external_id=item.text, count=int(item.attrib["count"]))
            for item in elem]


def _parse_drilldowns_tech_format(elem):
    return _parse_aggregate_field_drilldowns(elem, MIME_TYPE_TECH_FORMAT)


def _parse_drilldowns_custom_theme(elem):
    return _parse_aggregate_field_drilldowns(elem, DISCIPLINE_CUSTOM_THEME)


def _parse_aggregate_field_drilldowns(elem, aggregate_field_map):
    fields = dict()
    for item in elem:
        item_id = item.text
        field_id = aggregate_field_map.get(item_id)
        if not field_id:
            continue
        fields[field_id] = fields.get(field_id, 0) + int(item.attrib["count"])

    fields = sorted(fields.items(), key=lambda kv: kv[1], reverse=True)
    return [dict(external_id=k, count=v) for k, v in fields]


def _find_elem_text(root, elem_path):
    rv = _find_elems_text(root, elem_path)
    return rv[0] if rv else None


def _find_elems_text(root, elem_path):
    elements = root.findall(elem_path, namespaces=_NS)
    return [e.text for e in elements]


def _parse_item_list(root, items_path, item_handler):
    items = root.find(items_path, namespaces=_NS)
    if not items:
        return []
    return [item_handler(e) for e in items]
