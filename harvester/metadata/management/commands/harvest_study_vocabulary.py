import logging
import pandas as pd
from django.core.management.base import BaseCommand
from metadata.utils.translate import translate_with_deepl
from metadata.models import StudyVocabularyResource, MetadataField, MetadataTranslation, MetadataValue
from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor


logger = logging.getLogger("harvester")


def get_or_create_metadata_value(term, field, parent):
    try:
        return MetadataValue.objects.get(value=str(term["value"]))
    except MetadataValue.DoesNotExist:
        pass

    vocabulary = MetadataValue(value=term["value"], is_manual=True)
    translation = MetadataTranslation.objects.create(
        nl=term["name"],
        en=translate_with_deepl(term["name"]),
        is_fuzzy=True
    )
    vocabulary.translation = translation
    vocabulary.field = field
    vocabulary.name = term["name"]
    vocabulary.parent = parent
    vocabulary.save()
    return vocabulary


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
            en="study_vocabulary",
            is_fuzzy=True
        )
        field, _ = MetadataField.objects.get_or_create(
            name="study_vocabulary",
            defaults={"translation": field_translation, "is_manual": True, "is_hidden": True}
        )

        if vocabulary is not None:
            self.export_vocabulary(key=vocabulary, field=field)
        else:
            for key in self.domain_dictionary:
                self.export_vocabulary(key=key, field=field)

    def export_vocabulary(self, key, field):

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
        vocab_frame = pd.DataFrame.from_records(searched_source)
        # This drops the object that indicates the context of the vocabulary.
        vocab_frame = vocab_frame.dropna(subset=["language", "name"])
        # Nodes without parent should have root as parent.
        vocab_frame = vocab_frame.fillna(value="root")
        vocab_frame = vocab_frame.astype("string")
        vocab_frame = vocab_frame.reset_index(drop=True)
        vocab_groups = vocab_frame.groupby("parent_id").groups
        root = get_or_create_metadata_value(field=field, term=self.domain_dictionary[key], parent=None)
        for sub_root in vocab_groups["root"].tolist():
            self.depth_first_algorithm(value=sub_root, parent=root, field=field, groups=vocab_groups,
                                       frame=vocab_frame, output_list=[])

        logger.info('Done with study vocabulary harvest: ' + key)

    def depth_first_algorithm(self, value, parent, field, groups, frame, output_list):
        new_term = get_or_create_metadata_value(term=frame.iloc[value], field=field, parent=parent)
        output_list.append(new_term)
        try:
            for sub_values in groups[frame.iloc[value].value].tolist():
                output_list = self.depth_first_algorithm(sub_values, new_term, field, groups, frame, output_list)
        except KeyError:
            pass
        return output_list
