import logging
import pandas as pd
from django.core.management.base import BaseCommand
from metadata.utils.translate import translate_with_deepl
from metadata.models import StudyVocabularyResource, MetadataField, MetadataTranslation, MetadataValue
from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor
import ipdb;

logger = logging.getLogger("harvester")


def create_metadata_value(term, field, parent):
    if not MetadataValue.objects.filter(value=term["name"]).exists():
        vocabulary = MetadataValue(value=term["value"])
        translation = MetadataTranslation.objects.create(
            nl=term["name"],
            en=translate_with_deepl(term["name"])
        )
        vocabulary.translation = translation
        vocabulary.field = field
        vocabulary.name = str(term["name"])
        vocabulary.parent = parent
        return vocabulary
    else:
        return MetadataValue.objects.get(value=term["name"])


class Command(BaseCommand):

    domain_dictionary = {
        "applied-science": {
            "path": "applied-science/applied-science-2021.skos.json",
            "nl": "Toegepaste Wetenschappen",
            "en": "Applied Science",
            "value": "applied_science",
            "name": "applied_science",
            "language": "nl"
        },
        "informatievaardigheid": {
            "path": "informatievaardigheid/informatievaardigheid-2020.skos.json",
            "nl": "Informatievaardigheid",
            "en": "Information literacy",
            "value": "informatievaardigheid",
            "name": "informatievaardigheid",
            "language": "nl"
        },
        "vaktherapie": {
            "path": "vaktherapie/vaktherapie-2020.skos.json",
            "nl": "Vaktherapie",
            "en": "Information literacy",
            "value": "vaktherapie",
            "name": "vaktherapie",
            "language": "nl"
        },
        "verpleegkunde": {
            "path": "verpleegkunde/verpleegkunde-2019.skos.json",
            "nl": "Verpleegkunde",
            "en": "Nursing",
            "value": "verpleegkunde",
            "name": "verpleegkunde",
            "language": "nl"
        }
    }

    def handle(self, **options):

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

        field_translation, _ = MetadataTranslation.objects.get_or_create(
            nl="Vakvocabulaire",
            en="Study vocabulary"
        )
        field, _ = MetadataField.objects.get_or_create(
            name="Vakvocabulaire",
            defaults={"translation": field_translation}
        )

        vocabulary_list = []

        for key in self.domain_dictionary:
            raw_source = StudyVocabularyResource().get(self.domain_dictionary[key]["path"])
            searched_source = extractor.extract(*raw_source.content)
            vocab_frame = pd.DataFrame.from_records(searched_source).fillna("root")
            vocab_groups = vocab_frame.groupby("parent_id").groups
            root = create_metadata_value(field=field, term=self.domain_dictionary[key], parent=None)
            root.save()
            for sub_root in vocab_groups["root"].tolist():
                self.depth_first_algorithm(value=sub_root, parent=root, field=field, groups=vocab_groups,
                                           frame=vocab_frame, output_list=vocabulary_list)
        logger.info('Done with study vocabulary harvest')

    def depth_first_algorithm(self, value, parent, field, groups, frame, output_list):
        new_term = create_metadata_value(term=frame.iloc[value], field=field, parent=parent)
        new_term.save()
        output_list.append(new_term)
        try:
            for sub_values in groups[frame.iloc[value].value].tolist():
                print("Check")
                output_list = self.depth_first_algorithm(sub_values, new_term, field, groups, frame, output_list)
        finally:
            return output_list
