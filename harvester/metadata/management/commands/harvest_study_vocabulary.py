import logging
import pandas as pd
from django.core.management.base import BaseCommand
from metadata.utils.translate import translate_with_deepl
from metadata.models import StudyVocabularyResource, MetadataField, MetadataTranslation, MetadataValue
from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor
logger = logging.getLogger("harvester")


class Command(BaseCommand):

    domain_dictionary = {
        "applied-science": {
            "path": "applied-science/applied-science-2021.skos.json",
            "nl": "Toegepaste Wetenschappen",
            "en": "Applied Science",
            "value": "applied_science"
        },
        "informatievaardigheid": {
            "path": "informatievaardigheid/informatievaardigheid-2020.skos.json",
            "nl": "Informatievaardigheid",
            "en": "Information literacy",
            "value": "informatievaardigheid"
        },
        "vaktherapie": {
            "path": "vaktherapie/vaktherapie-2020.skos.json",
            "nl": "Vaktherapie",
            "en": "Information literacy",
            "value": "vaktherapie"
        },
        "verpleegkunde": {
            "path": "verpleegkunde/verpleegkunde-2019.skos.json",
            "nl": "Verpleegkunde",
            "en": "Nursing",
            "value": "verpleegkunde"
        }
    }
    def handle(self, **options):

        vocabulary_list = []

        config = create_config("extract_processor", {
            "objective": {
                "@": "$.@graph",
                "value": "$.@id",
                "parent_id": "$.skos:broader.@id",
                "language": "$.skos:prefLabel.@language",
                "name": "$.skos:prefLabel.@value"
            }
        })

        extractor = ExtractProcessor(config=config)

        for key in self.domain_dictionary:
            raw_source = StudyVocabularyResource().get(self.domain_dictionary[key])
            if key == "verpleegkunde":
                content_type, data = raw_source.content
                from pprint import pprint;pprint(list(filter(lambda node: node["@id"] == "urn:uuid:379e64f5-b618-4f3c-b037-f2684311c384", data["@graph"])))
            searched_source = extractor.extract(*raw_source.content)
            vocabulary_list.append(searched_source)

        field_translation, _ = MetadataTranslation.objects.get_or_create(
            nl="Vakvocabulaire",
            en="Study vocabulary"
        )
        field, _ = MetadataField.objects.get_or_create(
            name="Vakvocabulaire",
            defaults={"translation": field_translation}
        )

        to_add_vocabulary = []

        for vocab in vocabulary_list:
            vocab_frame = pd.DataFrame.from_records(vocab).fillna("root")
            vocab_groups = vocab_frame.groupby("parent_id").groups

            import ipdb; ipdb.set_trace()
            #toDo: Instead of a for loop for the vocabs, implement depth first sorting algorithm
            for term in vocab:
                #toDo: refactor, extract this as private function
                if not MetadataValue.objects.filter(value=term["name"]).exists():
                    # toDo: add check for duplicates in to_add_vocabulary
                    new_vocabulary = MetadataValue(value=term["value"])
                    if term["language"] == "nl":
                        new_vocabulary.translation = MetadataTranslation(
                            nl=term["name"],
                            en=translate_with_deepl(term["name"])
                        ).save()
                    else:
                        from pprint import pprint; pprint(term)
                    new_vocabulary.field = field
                    new_vocabulary.name = str(term["name"])
                    new_vocabulary.parent = term["parent_id"]
                    to_add_vocabulary.append(new_vocabulary)

        MetadataValue.objects.bulk_create(to_add_vocabulary)
        logger.info('Done with study vocabulary harvest')
