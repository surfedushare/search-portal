from collections import Iterator, defaultdict

from django.db import models
from django.db.models import Q

from datagrowth.datatypes import CollectionBase, DocumentCollectionMixin
from datagrowth.utils import ibatch


class Collection(DocumentCollectionMixin, CollectionBase):
    """
    Represents a set as used by the OAI-PMH protocol.
    These sets are logically collections of documents.

    N.B.: Collection has a special meaning within the search portal.
    They are manually curated groups of learning materials.
    """

    dataset = models.ForeignKey("Dataset", blank=True, null=True, on_delete=models.CASCADE)
    dataset_version = models.ForeignKey("DatasetVersion", blank=True, null=True, on_delete=models.CASCADE)

    def init_document(self, data, collection=None):
        doc = super().init_document(data, collection=collection or self)
        doc.dataset_version = self.dataset_version
        return doc

    def __str__(self):
        return "{} (id={})".format(self.name, self.id)

    def update(self, data, by_property, batch_size=32, collection=None):
        """
        Update data to the Collection in batches, using a property value to identify which Documents to update.
        Ported from Datagrowth 0.17. Best removed when updating to Django 3.2 and Datagrowth 0.17.
        """
        collection = collection or self
        Document = collection.get_document_model()
        assert isinstance(data, (Iterator, list, tuple,)), \
            f"Collection.update expects data to be formatted as iteratable not {type(data)}"

        count = 0
        for updates in ibatch(data, batch_size=batch_size):
            # We bulk update by getting all objects whose property matches
            # any update's "by_property" property value and then updating these source objects.
            # One update object can potentially target multiple sources
            # if multiple objects with the same value for the by_property property exist.
            updated = {}
            sources_by_lookup = defaultdict(list)
            for update in updates:
                sources_by_lookup[update[by_property]].append(update)
            target_filters = Q()
            for lookup_value in sources_by_lookup.keys():
                target_filters |= Q(**{f"properties__{by_property}": lookup_value})
            for target in collection.documents.filter(target_filters):
                for update_value in sources_by_lookup[target.properties[by_property]]:
                    target.update(update_value, commit=False)
                count += 1
                updated[target.properties[by_property]] = target
            Document.objects.bulk_update(
                updated.values(),
                ["properties", "identity", "reference"],
                batch_size=batch_size
            )
            # After all updates we add all data that hasn't been used in any update operation
            additions = []
            for lookup_value, sources in sources_by_lookup.items():
                if lookup_value not in updated:
                    additions += sources
            if len(additions):
                count += self.add(additions, batch_size=batch_size, collection=collection)

        return count
