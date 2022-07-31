NL_MATERIAL = {
    "math": {
        "title": "Didactiek van wiskundig denken",
        "text": "Leermateriaal over wiskunde en didactiek op de universiteit.",
        "url": "https://maken.wikiwijs.nl/91192/Wiskundedidactiek_en_ICT",
        "files": [
            [{
                "mime_type": "application/x-zip",
                "url": "https://maken.wikiwijs.nl/91192/Wiskundedidactiek_en_ICT",
                "title": "Wiskundedidactiek_en_ICT"
            }]
        ],
        "description":
        "Materiaal voor lerarenopleidingen en professionaliseringstrajecten gericht op wiskundedidactiek en ICT "
        "met Theo van den Bogaart",
        "language": "nl",
        "title_plain": "Wiskunde en Didactiek",
        "text_plain": "Leermateriaal over wiskunde en didactiek op de universiteit.",
        "external_id": "3522b79c-928c-4249-a7f7-d2bcb3077f10",
        "copyright": "cc-by-30",
        "lom_educational_levels": ["HBO"],
        "publisher_date": "2017-04-16T22:35:09+02:00",
        "keywords": ["nerds"],
        "authors": [{"name": "Michel van Ast"}, {"name": "Theo van den Bogaart"}, {"name": "Marc de Graaf"}],
        "publishers": ["Wikiwijs Maken"],
        "studies": ["7afbb7a6-c29b-425c-9c59-6f79c845f5f0"],
        "harvest_source": "wikiwijsmaken",
        "has_parts": [],
        "is_part_of": [],
        "suggest_phrase": "Leermateriaal over wiskunde en didactiek op de universiteit.",
        "suggest_completion": ["Leermateriaal", "over", "wiskunde", "en", "didactiek", "op", "de", "universiteit."],
        "analysis_allowed": True,
        "ideas": [],
        "doi": None,
        "technical_type": "document",
        "learning_material_disciplines": ["exact_informatica"],
        "learning_material_disciplines_normalized": ["exact_informatica"]
    },
    "biology": {
        "title": "Didactiek van biologisch denken",
        "text": "Leermateriaal over biologie en didactiek op de universiteit.",
        "url": "https://maken.wikiwijs.nl/91192/Biologiedidactiek_en_ICT",
        "files": [
            [{
                "mime_type": "application/x-zip",
                "url": "https://maken.wikiwijs.nl/91192/Biologiedidactiek_en_ICT",
                "title": "Biologiedidactiek_en_ICT"
            }]
        ],
        "description":
            "Materiaal voor lerarenopleidingen en professionaliseringstrajecten gericht op biologiedidactiek en ICT "
            "met Theo van den Bogaart",
        "language": "nl",
        "title_plain": "Biologie en Didactiek",
        "text_plain": "Leermateriaal over biologie en didactiek op de universiteit.",
        "external_id": "wikiwijs:123",
        "copyright": "cc-by-30",
        "lom_educational_levels": ["HBO"],
        "publisher_date": "2017-04-16T22:35:09+02:00",
        "keywords": [],
        "authors": [{"name": "Michel van Ast"}],
        "publishers": ["Wikiwijs Maken"],
        "studies": [],
        "harvest_source": "wikiwijsmaken",
        "has_parts": [],
        "is_part_of": [],
        "suggest_phrase": "Leermateriaal over biologie en didactiek op de universiteit.",
        "suggest_completion": ["Leermateriaal", "over", "biologie", "en", "didactiek", "op", "de", "universiteit."],
        "analysis_allowed": True,
        "ideas": [],
        "doi": None,
        "technical_type": "document",
        "learning_material_disciplines": ["aarde_milieu"],
        "learning_material_disciplines_normalized": ["aarde_milieu"]
    }
}


def generate_nl_material(educational_levels=None, title=None, description=None, technical_type=None, source=None,
                         copyright=None, publisher_date=None, studies=None, topic="math", external_id=None):
    copy = NL_MATERIAL[topic].copy()
    if title:
        copy["title"] = title
    if description:
        copy["description"] = description
    if external_id:
        copy["external_id"] = external_id
    if educational_levels:
        copy["lom_educational_levels"] = educational_levels
    if technical_type:
        copy["technical_type"] = technical_type
    if source:
        copy["harvest_source"] = source
    if copyright:
        copy["copyright"] = copyright
    if publisher_date:
        copy["publisher_date"] = publisher_date
    if studies:
        copy["studies"] = studies
    return copy
