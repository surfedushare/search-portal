NL_MATERIAL = {
    "math": {
        "title": "Didactiek van wiskundig denken",
        "text": "Leermateriaal over wiskunde en didactiek op de universiteit.",
        "url": "https://maken.wikiwijs.nl/91192/Wiskundedidactiek_en_ICT",
        "description":
        "Materiaal voor lerarenopleidingen en professionaliseringstrajecten gericht op wiskundedidactiek en ICT",
        "language": "nl",
        "title_plain": "Wiskunde en Didactiek",
        "text_plain": "Leermateriaal over wiskunde en didactiek op de universiteit.",
        "external_id": "surf:oai:surfsharekit.nl:3522b79c-928c-4249-a7f7-d2bcb3077f10",
        "copyright": "cc-by-30",
        "lom_educational_levels": ["HBO"],
        "publisher_date": "2017-04-16T22:35:09+02:00",
        "keywords": ["nerds"],
        "authors": ["Michel van Ast", "Theo van den Bogaart", "Marc de Graaf"],
        "publishers": ["Wikiwijs Maken"],
        "file_type": "text",
        "disciplines": ["7afbb7a6-c29b-425c-9c59-6f79c845f5f0"],
        "oaipmh_set": "wikiwijsmaken",
        "has_parts": [],
        "is_part_of": None,
        "suggest_phrase": "Leermateriaal over wiskunde en didactiek op de universiteit.",
        "suggest_completion": ["Leermateriaal", "over", "wiskunde", "en", "didactiek", "op", "de", "universiteit."],
        "analysis_allowed": True,
        "ideas": []
    },
    "biology": {
        "title": "Didactiek van biologisch denken",
        "text": "Leermateriaal over biologie en didactiek op de universiteit.",
        "url": "https://maken.wikiwijs.nl/91192/Biologiedidactiek_en_ICT",
        "description":
            "Materiaal voor lerarenopleidingen en professionaliseringstrajecten gericht op biologiedidactiek en ICT",
        "language": "nl",
        "title_plain": "Biologie en Didactiek",
        "text_plain": "Leermateriaal over biologie en didactiek op de universiteit.",
        "external_id": "surf:oai:surfsharekit.nl:3522b79c-4249-928c-a7f7-d2bcb3077f10",
        "copyright": "cc-by-30",
        "lom_educational_levels": ["HBO"],
        "publisher_date": "2017-04-16T22:35:09+02:00",
        "keywords": [],
        "authors": ["Michel van Ast"],
        "publishers": ["Wikiwijs Maken"],
        "file_type": "text",
        "disciplines": [],
        "oaipmh_set": "wikiwijsmaken",
        "has_parts": [],
        "is_part_of": None,
        "suggest_phrase": "Leermateriaal over biologie en didactiek op de universiteit.",
        "suggest_completion": ["Leermateriaal", "over", "biologie", "en", "didactiek", "op", "de", "universiteit."],
        "analysis_allowed": True,
        "ideas": []
    }
}


def generate_nl_material(educational_levels=None, file_type=None, source=None, copyright=None, publisher_date=None,
                         disciplines=None, topic="math"):
    copy = NL_MATERIAL[topic].copy()
    if educational_levels:
        copy["lom_educational_levels"] = educational_levels
    if file_type:
        copy["file_type"] = file_type
    if source:
        copy["oaipmh_set"] = source
    if copyright:
        copy["copyright"] = copyright
    if publisher_date:
        copy["publisher_date"] = publisher_date
    if disciplines:
        copy["disciplines"] = disciplines
    return copy
