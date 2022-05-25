import requests
import re

from django.core.management.base import BaseCommand

from metadata.models import MetadataValue


uuid4hex = re.compile('(?P<uuid>[0-9a-f]{8}\-[0-9a-f]{4}\-4[0-9a-f]{3}\-[89ab][0-9a-f]{3}\-[0-9a-f]{12})', re.I)


class Command(BaseCommand):

    @staticmethod
    def _get_node_label(node):
        return node.get("skos:prefLabel", node.get("dcterms:title", {}))["@value"]

    @staticmethod
    def _get_node_id(node):
        identifier_match = uuid4hex.search(node["@id"])
        return identifier_match.group(0)

    def _analyze_vocabulary_graph(self, vocabulary_path, graph):
        table = {}
        missing = set()
        found = set()
        for node in graph:
            identifier = self._get_node_id(node)
            table[identifier] = node
            mptt_node = MetadataValue.objects.filter(value=identifier).last()
            if mptt_node:
                found.add(identifier)
                continue
            mptt_node = MetadataValue.objects.filter(translation__nl=self._get_node_label(node))
            if mptt_node:
                found.add(identifier)
            else:
                missing.add(identifier)

        print("Graph analyze:", vocabulary_path)
        print("found", len(found))
        print("missing", len(missing))
        print("*"*80)

    def _substract_vocabulary_metadata(self, graph, ideas, disciplines):
        for node in graph:
            identifier = self._get_node_id(node)
            label = self._get_node_label(node)
            ideas.pop(identifier, None)
            ideas.pop(label, None)
            disciplines.pop(identifier, None)
            disciplines.pop(label, None)

    def handle(self, **options):
        ideas = {
            value.value: value
            for value in MetadataValue.objects.filter(field__name="ideas.keyword")
        }
        disciplines = {
            value.value: value
            for value in MetadataValue.objects.filter(field__name="disciplines")
        }
        vocabularies = [
            "verpleegkunde/verpleegkunde-2019.skos.json",
            "informatievaardigheid/informatievaardigheid-2020.skos.json",
            "vaktherapie/vaktherapie-2020.skos.json"
        ]
        for vocabulary_path in vocabularies:
            vocabulary_response = requests.get(f"https://vocabulaires.edurep.nl/type/vak/{vocabulary_path}")
            vocabulary = vocabulary_response.json()
            self._analyze_vocabulary_graph(vocabulary_path, vocabulary["@graph"])
            self._substract_vocabulary_metadata(vocabulary["@graph"], ideas, disciplines)
        print("Metadata analyze")
        print(
            "orphan ideas percentage",
            int(len(ideas) / MetadataValue.objects.filter(field__name="ideas.keyword").count() * 100)
        )
        print(
            "orphan disciplines percentage",
            int(len(disciplines) / MetadataValue.objects.filter(field__name="disciplines").count() * 100)
        )
