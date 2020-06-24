import os
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

from django.db import models

from datagrowth import settings as datagrowth_settings
from datagrowth.datatypes import CollectionBase, DocumentCollectionMixin


class Dataset(DocumentCollectionMixin, CollectionBase):
    """
    The most overarching model for storing learning materials.
    It's assumed that any Documents within a single Dataset have a similar schema.
    Meaning that any key in a Document's properties will be present in any other Document of the same Dataset.
    """

    is_active = models.BooleanField(default=False)

    def init_document(self, data, collection=None):
        doc = super().init_document(data, collection=collection)
        doc.dataset = self
        return doc

    def __str__(self):
        return "{} (id={})".format(self.name, self.id)

    @classmethod
    def get_name(cls):  # adheres to Datagrowth protocol for easy data loads
        return "dataset"

    def reset(self):
        self.collection_set.all().delete()
        for harvest in self.oaipmhharvest_set.all():
            harvest.reset()

    def get_elastic_indices(self):
        return ",".join([index.remote_name for index in self.indices.all()])

    def get_earliest_harvest_date(self):
        latest_harvest = self.oaipmhharvest_set.order_by("harvested_at").first()
        return latest_harvest.harvested_at if latest_harvest else None

    def get_elastic_documents_by_language(self, since):
        by_language = defaultdict(list)
        for arrangement in self.arrangement_set.prefetch_related("document_set").filter(modified_at__gte=since):
            languages = {doc.get_language() for doc in arrangement.documents.all()}
            if len(languages) != 1:
                by_language["unk"].append(arrangement.to_search())
                continue
            language = languages.pop()
            by_language[language].append(arrangement.to_search())
        return by_language

    def get_documents_by_language(self, minimal_educational_level=-1):
        by_language = defaultdict(list)
        for doc in self.documents.all():
            if doc.properties.get("lowest_educational_level", -1) < minimal_educational_level:
                continue
            language = doc.get_language()
            by_language[language].append(doc)
        return by_language

    def create_tfidf_vectorizers(self):
        if not self.name:
            raise ValueError("Can't create a vectorizer without a dataset name")
        dst = os.path.join(datagrowth_settings.DATAGROWTH_DATA_DIR, self.name)
        os.makedirs(dst, exist_ok=True)

        for language, docs in self.get_documents_by_language().items():
            vec = TfidfVectorizer(max_df=0.7)
            vec.fit_transform([doc.properties["text"] for doc in docs if doc.properties["text"]])
            joblib.dump(vec, os.path.join(dst, f"tfidf.{language}.pkl"))

    def get_tfidf_vectorizer(self, language):
        src = os.path.join(datagrowth_settings.DATAGROWTH_DATA_DIR, self.name, f"tfidf.{language}.pkl")
        vec = None
        try:
            vec = joblib.load(src)
        except FileNotFoundError:
            pass
        return vec
