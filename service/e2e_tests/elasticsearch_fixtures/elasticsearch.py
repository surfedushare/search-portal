NL_MATERIAL = {
    "title": "Didactiek van wiskundig denken",
    "text": "Leermateriaal over wiskunde en didactiek op de universiteit.",
    "url": "https://maken.wikiwijs.nl/91192/Wiskundedidactiek_en_ICT",
    "description": "Materiaal voor lerarenopleidingen en professionaliseringstrajecten gericht op wiskundedidactiek en ICT",
    "language": "nl",
    "title_plain": "Wiskunde en Didactiek",
    "text_plain": "Leermateriaal over wiskunde en didactiek op de universiteit.",
    "external_id": "surf:oai:surfsharekit.nl:3522b79c-928c-4249-a7f7-d2bcb3077f10",
    "copyright": "cc-by-30",
    "lom_educational_levels": ["HBO"],
    "publisher_date": "2017-04-16T22:35:09+02:00",
    "keywords": [],
    "authors": ["Michel van Ast", "Theo van den Bogaart", "Marc de Graaf"],
    "publishers": ["Wikiwijs Maken"],
    "file_type": "text",
    "disciplines": [],
    "arrangement_collection_name": "wikiwijsmaken",
    "has_part": [],
    "is_part_of": None,
    "suggest_phrase": "Leermateriaal over wiskunde en didactiek op de universiteit.",
    "suggest_completion": "Leermateriaal over wiskunde en didactiek op de universiteit.",
}


def generate_nl_material(educational_levels=None, file_type=None, source=None):
    copy = NL_MATERIAL.copy()
    if educational_levels:
        copy["lom_educational_levels"] = educational_levels
    if file_type:
        copy["file_type"] = file_type
    if source:
        copy["arrangement_collection_name"] = source
    return copy
