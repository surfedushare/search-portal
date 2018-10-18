from xml.etree import ElementTree as ET

_NS = {
    "srw": "http://www.loc.gov/zing/srw/",
    "diag": "http://www.loc.gov/zing/srw/diagnostic/",
    "xcql": "http://www.loc.gov/zing/cql/xcql/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "meresco_srw": "http://meresco.org/namespace/srw#",
    "dd": "http://meresco.org/namespace/drilldown"
}


def parse_response(xml_text):
    root = ET.fromstring(xml_text)
    return dict(number_of_records=_parse_number_of_records(root),
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
            for item in dd:
                rv.setdefault(term_id, list()).append(
                    dict(item_id=item.text, item_count=item.attrib["count"]))
    except Exception:
        pass
    return rv


