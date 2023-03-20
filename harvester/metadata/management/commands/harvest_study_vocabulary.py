import logging
import pandas as pd
from django.core.management.base import BaseCommand
from metadata.utils.translate import translate_with_deepl
from metadata.models import StudyVocabularyResource, MetadataField, MetadataTranslation, MetadataValue
from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor

logger = logging.getLogger("harvester")


def get_or_create_metadata_value(term, field, parent):
    if not MetadataValue.objects.filter(value=str(term["value"])).exists():
        vocabulary = MetadataValue(value=term["value"])
        translation = MetadataTranslation.objects.create(
            nl=term["name"],
            en=translate_with_deepl(term["name"])
        )
        vocabulary.translation = translation
        vocabulary.field = field
        vocabulary.name = str(term["name"])
        vocabulary.parent = parent
        vocabulary.save()
        return vocabulary
    else:
        return MetadataValue.objects.get(value=str(term["value"]))


class Command(BaseCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--vocabulary',
                            choices=["applied-science", "informatievaardigheid", "vaktherapie", "verpleegkunde"])

    domain_dictionary = {
        "applied-science": {
            "path": "applied-science/applied-science-2021.skos.json",
            "nl": "Toegepaste Wetenschappen",
            "en": "Applied Science",
            "value": "applied-science",
            "name": "applied-science",
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

        vocabulary = options["vocabulary"]

        field_translation, _ = MetadataTranslation.objects.get_or_create(
            nl="vakvocabulaire",
            en="study_vocabulary"
        )
        field, _ = MetadataField.objects.get_or_create(
            name="study_vocabulary",
            defaults={"translation": field_translation}
        )

        vocabulary_list = []
        if vocabulary is not None:
            self.export_vocabulary(key=vocabulary, field=field, output_list=vocabulary_list)
        else:
            for key in self.domain_dictionary:
                self.export_vocabulary(key=key, field=field, output_list=vocabulary_list)

    def export_vocabulary(self, key, field, output_list):

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

        raw_source = StudyVocabularyResource().get(self.domain_dictionary[key]["path"])
        raw_source.close()
        searched_source = extractor.extract(*raw_source.content)
        vocab_frame = pd.DataFrame.from_records(searched_source).fillna("root")
        vocab_groups = vocab_frame.groupby("parent_id").groups
        root = get_or_create_metadata_value(field=field, term=self.domain_dictionary[key], parent=None)
        for sub_root in vocab_groups["root"].tolist():
            self.depth_first_algorithm(value=sub_root, parent=root, field=field, groups=vocab_groups,
                                       frame=vocab_frame, output_list=output_list)

        logger.info('Done with study vocabulary harvest: ' + key)

    def depth_first_algorithm(self, value, parent, field, groups, frame, output_list):
        new_term = get_or_create_metadata_value(term=frame.iloc[value], field=field, parent=parent)
        output_list.append(new_term)
        try:
            for sub_values in groups[frame.iloc[value].value].tolist():
                output_list = self.depth_first_algorithm(sub_values, new_term, field, groups, frame, output_list)
        finally:
            return output_list
