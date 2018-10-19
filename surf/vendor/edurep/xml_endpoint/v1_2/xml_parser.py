from xml.etree import ElementTree as ET

from surf.vendor.edurep.xml_endpoint.v1_2.choices import MIME_TYPE_TECH_FORMAT

_NS = {
    "srw": "http://www.loc.gov/zing/srw/",
    "diag": "http://www.loc.gov/zing/srw/diagnostic/",
    "xcql": "http://www.loc.gov/zing/cql/xcql/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "meresco_srw": "http://meresco.org/namespace/srw#",
    "dd": "http://meresco.org/namespace/drilldown"
}

_TECH_FORMAT_LOM = "lom.technical.format"


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
    records = root.find("srw:records", namespaces=_NS)
    if not records:
        return []
    return [_parse_record(e) for e in records]


def _parse_record(elem):
    return elem.text


def _parse_drilldowns(root):
    rv = dict()
    try:
        ext_data = root.find("srw:extraResponseData", namespaces=_NS)
        drilldowns = ext_data.find("dd:drilldown", namespaces=_NS)
        drilldowns = drilldowns.find("dd:term-drilldown", namespaces=_NS)
        for dd in drilldowns:
            term_id = dd.attrib["name"]
            if term_id == _TECH_FORMAT_LOM:
                rv[term_id] = _parse_drilldowns_tech_format(dd)
            else:
                rv[term_id] = _parse_drilldowns_term(dd)
    except Exception:
        pass
    return [dict(id=k, items=v) for k, v in rv.items()]


def _parse_drilldowns_term(elem):
    return [dict(id=item.text, count=int(item.attrib["count"]))
            for item in elem]


def _parse_drilldowns_tech_format(elem):
    items = dict()
    for item in elem:
        mime_type = item.text
        item_id = MIME_TYPE_TECH_FORMAT.get(mime_type)
        if not item_id:
            continue
        items[item_id] = items.get(item_id, 0) + int(item.attrib["count"])

    return [dict(id=k, count=v) for k, v in items.items()]
