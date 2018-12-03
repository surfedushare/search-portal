MIME_TYPE_TECH_FORMAT = {
    "application/x-yossymemo": "digiboard",
    "application/x-ibooks+zip": "ebook",
    "image/bmp": "image",
    "application/vnd.openxmlformats-officedocument.presentationml.pre": "presentation",
    "application/vnd.openxmlformats-officedocument.presentationml.sli": "presentation",
    "application/vnd.oasis.opendocument.spreadsheet": "spreadsheet",
    "application/postscript": "text",
    "application/vnd.ms-word": "text",
    "application/x-tar": "archive",
    "application/vnd.ms-word.document.macroEnabled.12": "text",
    "application/x-stuffit": "archive",
    "application/x-koan": "audio",
    "application/vnd.koan": "audio",
    "audio/midi": "audio",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.template": "text",
    "image/pjpeg": "image",
    "text/rtf": "text",
    "application/Inspire": "digiboard",
    "message/rfc822": "message",
    "video/quicktime": "video",
    "application/x-AS3PE": "digiboard",
    "application/vnd.ms-publisher": "text",
    "application/vnd.google-earth.kmz": "googleearth",
    "image/png": "image",
    "video/x-msvideo": "video",
    "application/ppt": "presentation",
    "application/x-rar-compressed": "archive",
    "application/rtf": "text",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "spreadsheet",
    "video/mpeg": "video",
    "image/x-icon": "image",
    "image/x-ms-bmp": "image",
    "application/x-pdf": "pdf",
    "image/tiff": "image",
    "application/vnd.openxmlformats-officedocument.presentationml.slideshow": "presentation",
    "application/x-java": "app",
    "image/jpg": "image",
    "application/x-Inspire": "digiboard",
    "application/x-smarttech-notebook": "digiboard",
    "application/x-zip-compressed": "digiboard",
    "application/x-ACTIVprimary3": "digiboard",
    "application/vnd.ms-excel": "spreadsheet",
    "text/plain": "text",
    "audio/x-wav": "audio",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "presentation",
    "application/x-mplayer2": "video",
    "image/gif": "image",
    "audio/mpeg": "audio",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "text",
    "video/mp4": "video",
    "application/vnd.ms-powerpoint": "presentation",
    "video/x-ms-wmv": "video",
    "video/x-flv": "video",
    "text/xml": "text",
    "application/msword": "text",
    "application/zip": "archive",
    "video/x-ms-asf": "video",
    "application/pdf": "pdf",
    "text/html": "text",
    "image/jpeg": "image",
    "application/x-Wikiwijs-Arrangement": "wikiwijsarrangement"
}

TECH_FORMAT_MIME_TYPES = dict()
for k, v in MIME_TYPE_TECH_FORMAT.items():
    TECH_FORMAT_MIME_TYPES.setdefault(v, []).append(k)

_DISCIPLINE_ENTRIES = [
    dict(id='2adcec22-095d-4937-aed7-48788080460b', theme='Aarde en milieu'),
    dict(id='e683a77c-f926-4c00-8e9e-e609cb93fc85', theme='Onderwijs en Opvoeding'),
    dict(id='455d527a-bfd0-4460-919e-12e0478a54cf', theme='Taal en Communicatie'),
    dict(id='8e080031-93e9-4c07-b4dc-73d5d096a2fe', theme='Exact en informatica'),
    dict(id='92161d11-91ce-48e2-b79a-8aa2df8b7022', theme='Economie en Bedrijf'),
    dict(id='cba3253b-ca4b-4bd5-bbf5-2cc90d910e57', theme='Recht en Bestuur'),
    dict(id='2b363227-8633-4652-ad57-c61f1efc02c8', theme='Aarde en milieu'),
    dict(id='652bc6a3-d024-493f-9199-a08340cbb2b3', theme='Techniek'),
    dict(id='1f7aa29f-38d8-4dab-91db-3be52669951f', theme='Taal en Communicatie'),
    dict(id='94a7654d-c145-4b9c-aab3-7dc478534437', theme='Techniek'),
    dict(id='3629ac98-42b8-47db-acb2-e37327042857', theme='Taal en Communicatie'),
    dict(id='4df72ecd-3928-4abb-b227-8abd451e4195', theme='Gedrag en Maatschappij'),
    dict(id='24850a94-16c6-4b87-8dce-a8b9a6673e5d', theme='Aarde en milieu'),
    dict(id='3b12504f-5600-42b7-aaf3-2b9fd011c093', theme='Gezondheid'),
    dict(id='7f772375-6e8e-43fe-9b08-d7f3971d8cc9', theme='Taal en Communicatie'),
    dict(id='81a1f605-db58-448d-a1dc-da682316c505', theme='Taal en Communicatie'),
    dict(id='4ba5583f-b147-42cc-a083-ce5ebfd53746', theme='Economie en Bedrijf'),
    dict(id='8cfb914a-ead0-4125-b389-d5d9816afb95', theme='Techniek'),
    dict(id='18f53978-1118-4051-a778-b8d7f60ca982', theme='Taal en Communicatie'),
    dict(id='d35b903f-1598-4bdd-a2fa-8aba854df762', theme='Kunst en Cultuur'),
    dict(id='9f4710e3-f173-404e-b12e-577657a5da04', theme='Taal en Communicatie'),
    dict(id='5c98610c-3f7d-4521-b231-d0932b4ca799', theme='Gezondheid'),
    dict(id='c001f86a-4f8f-4420-bd78-381c615ecedc', theme='Aarde en milieu'),
    dict(id='ef3a0b2e-0843-4e0a-b45b-788be6e1ec8d', theme='Kunst en Cultuur'),
    dict(id='596e13b2-5626-4312-8440-50e9bd7b4271', theme='Taal en Communicatie'),
    dict(id='3ddfe1f4-c8d8-44c7-92d0-8c3c5d6e51f5', theme='Onderwijs en Opvoeding'),
    dict(id='2845473d-ce18-450a-9135-6738abbdc129', theme='Exact en informatica'),
    dict(id='aedcfc1c-a676-4f40-8587-4a5f43a354b5', theme='Taal en Communicatie'),
    dict(id='8e3e2aab-1e36-4942-b86a-eba155353b23', theme='Kunst en Cultuur'),
    dict(id='db5b20c4-4e94-4554-8137-a45acb130ad2', theme='Aarde en milieu'),
    dict(id='315566f5-ca2c-4fb2-bf82-263ec13c9b75', theme='Techniek'),
    dict(id='20f264c8-a132-4b43-96dd-c661fd6bace7', theme='Aarde en milieu'),
    dict(id='7aa6f577-b02d-484a-90d6-72fc80199f9a', theme='Kunst en Cultuur'),
    dict(id='e98be5ad-4bd2-4768-a9eb-7e24026e360c', theme='Exact en informatica'),
    dict(id='3401cf6e-82e4-404c-b216-b980ff407159', theme='Taal en Communicatie'),
    dict(id='0861c43d-1874-4788-b522-df8be575677f', theme='Onderwijs en Opvoeding'),
    dict(id='03d65ce0-2fd7-4f16-91f1-dcdce873dffc', theme='Recht en Bestuur'),
    dict(id='86390768-492e-4d9e-8bfe-65648e79522a', theme='Onderwijs en Opvoeding'),
    dict(id='b922af97-b3a5-48ac-a01d-32ad5cab5abc', theme='Recht en Bestuur'),
    dict(id='dabf3753-248a-495b-b861-bcd36e2b55cb', theme='Taal en Communicatie'),
    dict(id='c6c55e80-9fae-440b-b50a-4a1f70432734', theme='Techniek'),
    dict(id='10169c87-c77a-4ab7-8c19-c79ba7865bbf', theme='Gedrag en Maatschappij'),
    dict(id='4449624e-dfcc-4414-958a-d770a168f637', theme='Recht en Bestuur'),
    dict(id='116fbfd6-77d8-4676-8634-8cfd686942c9', theme='Taal en Communicatie'),
    dict(id='3aab168a-9b24-4aca-b0f1-4bfb12e7c288', theme='Exact en informatica'),
    dict(id='6cfbea61-4877-4518-9b06-9f07146e139d', theme='Aarde en milieu'),
    dict(id='e5346879-4051-4ad9-bef8-2078620ef6cf', theme='Gedrag en Maatschappij'),
    dict(id='49b28e01-e836-408b-9cf2-2976f85312c7', theme='Gedrag en Maatschappij'),
    dict(id='952bf604-cc38-44e3-889a-a9e74a18da8e', theme='Taal en Communicatie'),
    dict(id='b3f61346-92c4-4fb5-9207-6a4142b64122', theme='Taal en Communicatie'),
    dict(id='b9a2c9ea-48f6-4218-b974-c14e84b00c1a', theme='Kunst en Cultuur'),
    dict(id='e605402f-4cc2-46bb-9026-d1d49bde17bf', theme='Kunst en Cultuur'),
    dict(id='e6ca634f-c1aa-4d03-9e26-4725a31887f1', theme='Techniek'),
    dict(id='9ca10565-ec88-44b7-abc2-582dfdea5abc', theme='Techniek'),
    dict(id='4c8a3378-6616-459d-acc4-83ee5a9b91a2', theme='Kunst en Cultuur'),
    dict(id='08018424-b218-4de6-b174-df6982e7a72d', theme='Economie en Bedrijf'),
    dict(id='693f235a-511f-4f59-9633-6b1abd0e3b6f', theme='Techniek'),
    dict(id='7afbb7a6-c29b-425c-9c59-6f79c845f5f0', theme='Exact en informatica'),
    dict(id='db5b20c4-4e94-4554-8137-a45acb130ad2', theme='Techniek')
]

DISCIPLINE_CUSTOM_THEME = dict()
CUSTOM_THEME_DISCIPLINES = dict()

for empty_theme in {"Interdisciplinair"}:
    CUSTOM_THEME_DISCIPLINES[empty_theme] = []

for d in _DISCIPLINE_ENTRIES:
    discipline_id, theme = d["id"], d["theme"]
    DISCIPLINE_CUSTOM_THEME.setdefault(discipline_id, []).append(theme)
    CUSTOM_THEME_DISCIPLINES.setdefault(theme, []).append(discipline_id)


CUSTOM_COPYRIGHTS = {
    "yes": {"external_ids": ["yes"],
            "title": "Restricted access"},
    "cc-by": {"external_ids": ["cc-by-30", "cc-by-40"],
              "title": "Naamsvermelding"},
    "cc-by-nc": {"external_ids": ["cc-by-nc-30", "cc-by-nc-40"],
                 "title": "Naamsvermelding-NietCmmercieel"},
    "cc-by-nc-nd": {"external_ids": ["cc-by-nc-nd-30", "cc-by-nc-nd-40"],
                    "title": "Naamsvermelding-NietCmmercieel-GeenAfgeleideWerken"},
    "cc-by-nc-sa": {"external_ids": ["cc-by-nc-sa-30", "cc-by-nc-sa-40"],
                    "title": "Naamsvermelding-NietCmmercieel-GelijkDelen"},
    "cc-by-nd": {"external_ids": ["cc-by-nd-30", "cc-by-nd-40"],
                 "title": "Naamsvermelding-GeenAfgeleideWerken"},
    "cc-by-sa": {"external_ids": ["cc-by-sa-30", "cc-by-sa-40"],
                 "title": "Naamsvermelding-GelijkDelen"},
}

EDUREP_COPYRIGHTS = dict()

for cc_id, cc_data in CUSTOM_COPYRIGHTS.items():
    for id in cc_data["external_ids"]:
        EDUREP_COPYRIGHTS[id] = cc_id
